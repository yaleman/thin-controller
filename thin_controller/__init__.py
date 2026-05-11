"""thin-controller init"""

import os
import re
from typing import Annotated, Dict, List

from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from loguru import logger
from pydantic import BaseModel

from thin_controller.ec2 import (
    STATE_CHANGES,
    get_managed_instance,
    list_managed_instances,
    start_instance,
    stop_instance,
)
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
        instance_data = get_managed_instance(instance_id, region)
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
            start_instance(instance_id, region)
        except ClientError as error:
            logger.error(f"Failed to start {instance_id=} {error=}")
            raise HTTPException(
                status_code=500, detail="An error occurred! See the backend logs."
            ) from error
    elif new_state == "stop":
        try:
            stop_instance(instance_id, region)
        except ClientError as error:
            logger.error("Failed to start instance_id={} error={}", instance_id, error)
            raise HTTPException(
                status_code=500, detail="An error occurred! See the backend logs."
            ) from error
    return RedirectResponse("/", 301)


@app.get("/api/instances")
def read_instances() -> Dict[str, List[AWSInstance]]:
    """instances"""
    try:
        instances = list_managed_instances(config.region_list())
    except NoCredentialsError as exc:
        raise HTTPException(
            status_code=500,
            detail="No AWS credentials found, something went wrong in the backend",
        ) from exc
    except Exception as error:
        logger.error("Failed to get instances error={}", error)
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
