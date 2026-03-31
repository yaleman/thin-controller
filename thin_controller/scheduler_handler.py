"""AWS Lambda handler for scheduled EC2 power control."""

from collections.abc import Mapping
from typing import Any, TypedDict

from botocore.exceptions import ClientError, NoCredentialsError
from loguru import logger

from thin_controller.ec2 import list_managed_instances, start_instance, stop_instance
from thin_controller.models import Config
from thin_controller.schedule import decide_schedule_action


class SchedulerSummary(TypedDict):
    """Result summary for a scheduler run."""

    status: str
    checked: int
    started: int
    stopped: int
    skipped: int
    errors: int


def handler(event: Mapping[str, Any], context: Any) -> SchedulerSummary:
    """Run the hourly scheduled power controller."""
    del event, context

    config = Config()
    summary: SchedulerSummary = {
        "status": "ok",
        "checked": 0,
        "started": 0,
        "stopped": 0,
        "skipped": 0,
        "errors": 0,
    }

    try:
        instances = list_managed_instances(config.region_list())
    except NoCredentialsError as error:
        logger.error("No AWS credentials found for scheduled power control: {}", error)
        raise

    for instance in instances:
        summary["checked"] += 1
        decision = decide_schedule_action(instance)
        if decision.action is None:
            summary["skipped"] += 1
            logger.debug(
                "Skipping instance_id={} region={} reason={}",
                instance.instance_id,
                instance.region,
                decision.reason,
            )
            continue

        try:
            if decision.action == "start":
                start_instance(instance.instance_id, instance.region)
                summary["started"] += 1
            elif decision.action == "stop":
                stop_instance(instance.instance_id, instance.region)
                summary["stopped"] += 1
        except ClientError as error:
            summary["errors"] += 1
            summary["status"] = "error"
            logger.error(
                "Failed scheduler action={} instance_id={} region={} error={}",
                decision.action,
                instance.instance_id,
                instance.region,
                error,
            )
            continue

        logger.info(
            "Scheduler action={} instance_id={} region={} reason={}",
            decision.action,
            instance.instance_id,
            instance.region,
            decision.reason,
        )

    return summary
