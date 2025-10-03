"""thin-controller init"""

import re
from typing import Annotated, Dict, List
import os

from loguru import logger
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from botocore.exceptions import NoCredentialsError, ClientError
from boto3.session import Session
from pydantic import BaseModel

from thin_controller.models import AWSInstance, Config


app = FastAPI()
config = Config()


@app.get("/")
def index() -> HTMLResponse:
    """homepage"""
    return HTMLResponse(
        open(
            os.path.join(os.path.dirname(__file__), "static/index.html"),
            encoding="utf-8",
        ).read()
    )


@app.get("/css/styles.css")
def css_styles() -> FileResponse:
    """css files"""
    return FileResponse(os.path.join(os.path.dirname(__file__), "static/styles.css"))


@app.get("/css/simple.min.css")
def css_simple() -> FileResponse:
    """css files"""
    return FileResponse(
        os.path.join(os.path.dirname(__file__), "static/simple.min.css")
    )


@app.get("/img/favicon.png")
def img_favicon() -> FileResponse:
    """favicon"""
    return FileResponse(os.path.join(os.path.dirname(__file__), "static/favicon.png"))


MANAGED_INSTANCE_TAG_FILTER = [
    {"Name": "tag:thin_controller_managed", "Values": ["true"]}
]

# what is the allowed state based on the current state?
STATE_CHANGES = {
    # pending
    "running": "stop",
    # shutting-down
    # terminated
    # stopping
    "stopped": "start",
}


@app.post("/api/instance")
def update_instance(
    instance_id: Annotated[str, Form()],
    new_state: Annotated[str, Form()],
    region: Annotated[str, Form()],
) -> RedirectResponse:
    """Update an instance"""
    # validate the instance ID is OK
    if not re.match(r"i-[0-9a-f]{17}", instance_id):
        raise HTTPException(400, "Invalid instance ID provided!")
    try:
        client = Session(region_name=region).client("ec2")

        # get that instance
        instances = client.describe_instances(
            InstanceIds=[instance_id], Filters=MANAGED_INSTANCE_TAG_FILTER
        )

        # see if it's OK
        instance_data = AWSInstance.model_validate(
            instances.get("Reservations", [])[0].get("Instances", [])[0]
        )
    except NoCredentialsError as exc:
        raise HTTPException(
            status_code=500,
            detail="No AWS credentials found, something went wrong in the backend",
        ) from exc
    except Exception as error:
        logger.error("Failed to get instances, region={} error={}", region, error)
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {error}"
        ) from error

    # check the state change is OK
    new_state_check = STATE_CHANGES.get(instance_data.state)
    if new_state_check is None:
        raise HTTPException(400, "Unknown state change requested!")
    # they asked for something wrong
    if new_state_check != new_state:
        raise HTTPException(400, "Invalid state change requested!")

    # do the thing
    if new_state == "start":
        try:
            response = client.start_instances(
                InstanceIds=[instance_id],
                DryRun=False,
            )
        except ClientError as error:
            logger.error(f"Failed to start {instance_id=} {error=}")
            raise HTTPException(
                status_code=500, detail="An error occurred! See the backend logs."
            ) from error

        if "Error" in response:
            logger.error(
                "Failed to start instance_id={} error={}",
                instance_id,
                response.get("Error"),
            )
            raise HTTPException(
                status_code=500, detail="An error occurred, check the logs!"
            )
    elif new_state == "stop":
        try:
            response = client.stop_instances(
                InstanceIds=[
                    instance_id,
                ],
                Hibernate=False,
                DryRun=False,
                Force=False,
            )
        except ClientError as error:
            logger.error("Failed to start instance_id={} error={}", instance_id, error)
            raise HTTPException(
                status_code=500, detail="An error occurred! See the backend logs."
            ) from error

        if "Error" in response:
            logger.error(
                "Failed to start instance_id={} error={}",
                instance_id,
                response.get("Error"),
            )
            raise HTTPException(
                status_code=500, detail="An error occurred, check the logs!"
            )
    return RedirectResponse("/", 301)


@app.get("/api/instances")
def read_instances() -> Dict[str, List[AWSInstance]]:
    """instances"""
    # filter based on tags

    instances = []
    # using boto3 list the instances
    for region in config.region_list():
        # get the instances

        try:
            region_instances = (
                Session(region_name=region)
                .client("ec2")
                .describe_instances(Filters=MANAGED_INSTANCE_TAG_FILTER)
            )
            for reservation in region_instances.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    instances.append(AWSInstance.model_validate(instance))
            # logger.debug("region={}, instances={}", region, region_instances)
            # logger.debug(json.dumps(region_instances, indent=4, default=str))
        except NoCredentialsError as exc:
            raise HTTPException(
                status_code=500,
                detail="No AWS credentials found, something went wrong in the backend",
            ) from exc
        except Exception as error:
            logger.error("Failed to get instances, region={} error={}", region, error)
            raise HTTPException(
                status_code=500, detail=f"An error occurred: {error}"
            ) from error

    return {"instances": instances}


class ApiConfig(BaseModel):
    """response for /api/config"""

    regions: List[str]


@app.get("/api/config")
def read_config() -> ApiConfig:
    """config dump"""
    val = config.model_dump(mode="json")
    val["regions"] = config.region_list()
    return ApiConfig.model_validate(val)


@app.get("/up")
def up() -> str:
    """simple "up" check"""
    return "OK"
