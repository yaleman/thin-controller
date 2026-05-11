"""Tests for the scheduled power control handler."""

from thin_controller.models import AWSInstance
from thin_controller.schedule import ScheduleDecision
from thin_controller.scheduler_handler import handler


def build_instance(instance_id: str, state: str, tags: dict[str, str]) -> AWSInstance:
    """Build a small instance model for scheduler tests."""
    return AWSInstance.model_validate(
        {
            "InstanceId": instance_id,
            "State": {"Name": state},
            "InstanceType": "t3.micro",
            "Tags": [{"Key": key, "Value": value} for key, value in tags.items()],
            "Placement": {"AvailabilityZone": "ap-southeast-2a"},
        }
    )


def test_scheduler_handler_starts_and_stops(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Scheduler applies start and stop actions."""
    instances = [
        build_instance(
            "i-0b12345042be12345",
            "running",
            {
                "thin-controller-timezone": "UTC",
                "thin-controller-on-hours": "22-06",
            },
        ),
        build_instance(
            "i-0b12345042be12346",
            "stopped",
            {
                "thin-controller-timezone": "UTC",
                "thin-controller-on-hours": "00-23",
            },
        ),
    ]
    actions: list[tuple[str, str]] = []

    monkeypatch.setattr(
        "thin_controller.scheduler_handler.list_managed_instances",
        lambda regions: instances,
    )
    monkeypatch.setattr(
        "thin_controller.scheduler_handler.decide_schedule_action",
        lambda instance: ScheduleDecision(
            action="stop" if instance.instance_id.endswith("45") else "start",
            reason="test action",
        ),
    )
    monkeypatch.setattr(
        "thin_controller.scheduler_handler.start_instance",
        lambda instance_id, region: actions.append(("start", instance_id)),
    )
    monkeypatch.setattr(
        "thin_controller.scheduler_handler.stop_instance",
        lambda instance_id, region: actions.append(("stop", instance_id)),
    )

    summary = handler({}, None)

    assert summary["checked"] == 2
    assert summary["started"] == 1
    assert summary["stopped"] == 1
    assert ("stop", "i-0b12345042be12345") in actions
    assert ("start", "i-0b12345042be12346") in actions


def test_scheduler_handler_skips_unconfigured_instances(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Instances without schedule tags are ignored."""
    monkeypatch.setattr(
        "thin_controller.scheduler_handler.list_managed_instances",
        lambda regions: [
            build_instance(
                "i-0b12345042be12345",
                "running",
                {"Name": "manual-instance"},
            )
        ],
    )
    monkeypatch.setattr(
        "thin_controller.scheduler_handler.decide_schedule_action",
        lambda instance: ScheduleDecision(
            action=None,
            reason="schedule tags not configured",
        ),
    )

    summary = handler({}, None)

    assert summary["checked"] == 1
    assert summary["skipped"] == 1
    assert summary["started"] == 0
    assert summary["stopped"] == 0
