"""Shared EC2 operations for the API and scheduler."""

from typing import List

from boto3.session import Session
from botocore.exceptions import ClientError

from thin_controller.models import AWSInstance

MANAGED_INSTANCE_TAG_FILTER = [
    {"Name": "tag:thin_controller_managed", "Values": ["true"]}
]

STATE_CHANGES = {
    "running": "stop",
    "stopped": "start",
}


def list_managed_instances(regions: List[str]) -> List[AWSInstance]:
    """List managed instances across all configured regions."""
    instances = []
    for region in regions:
        paginator = Session(region_name=region).client("ec2").get_paginator(
            "describe_instances"
        )
        for page in paginator.paginate(Filters=MANAGED_INSTANCE_TAG_FILTER):
            for reservation in page.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    instances.append(AWSInstance.model_validate(instance))
    return instances


def get_managed_instance(instance_id: str, region: str) -> AWSInstance:
    """Fetch a single managed instance by ID."""
    instances = (
        Session(region_name=region)
        .client("ec2")
        .describe_instances(
            InstanceIds=[instance_id],
            Filters=MANAGED_INSTANCE_TAG_FILTER,
        )
    )
    return AWSInstance.model_validate(
        instances.get("Reservations", [])[0].get("Instances", [])[0]
    )


def start_instance(instance_id: str, region: str) -> None:
    """Start an EC2 instance."""
    response = Session(region_name=region).client("ec2").start_instances(
        InstanceIds=[instance_id],
        DryRun=False,
    )
    if "Error" in response:
        raise ClientError(response, "StartInstances")


def stop_instance(instance_id: str, region: str) -> None:
    """Stop an EC2 instance politely."""
    response = Session(region_name=region).client("ec2").stop_instances(
        InstanceIds=[instance_id],
        Hibernate=False,
        DryRun=False,
        Force=False,
    )
    if "Error" in response:
        raise ClientError(response, "StopInstances")
