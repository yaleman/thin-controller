"""Tests for schedule parsing and evaluation."""

from datetime import datetime, timezone

import pytest

from thin_controller.models import AWSInstance
from thin_controller.schedule import (
    decide_schedule_action,
    is_hour_in_window,
    parse_on_hours,
)


def build_instance(state: str, tags: dict[str, str]) -> AWSInstance:
    """Build a small instance model for tests."""
    return AWSInstance.model_validate(
        {
            "InstanceId": "i-0b12345042be12345",
            "State": {"Name": state},
            "InstanceType": "t3.micro",
            "Tags": [{"Key": key, "Value": value} for key, value in tags.items()],
            "Placement": {"AvailabilityZone": "ap-southeast-2a"},
        }
    )


def test_parse_on_hours() -> None:
    """Parse a simple window."""
    assert parse_on_hours("09-17") == (9, 17)


def test_parse_on_hours_rejects_invalid_values() -> None:
    """Reject invalid schedule ranges."""
    with pytest.raises(ValueError):
        parse_on_hours("17-17")

    with pytest.raises(ValueError):
        parse_on_hours("09-24")


def test_is_hour_in_window_handles_overnight_ranges() -> None:
    """Overnight windows wrap across midnight."""
    assert is_hour_in_window(23, 22, 6) is True
    assert is_hour_in_window(4, 22, 6) is True
    assert is_hour_in_window(12, 22, 6) is False


def test_is_hour_in_window_uses_end_exclusive_boundaries() -> None:
    """The start hour is inclusive and the end hour is exclusive."""
    assert is_hour_in_window(9, 9, 17) is True
    assert is_hour_in_window(17, 9, 17) is False


def test_decide_schedule_action_starts_inside_window() -> None:
    """Stopped instances start inside the window."""
    instance = build_instance(
        "stopped",
        {
            "thin-controller-timezone": "Australia/Brisbane",
            "thin-controller-on-hours": "09-17",
        },
    )
    decision = decide_schedule_action(
        instance,
        now=datetime(2026, 3, 31, 0, 0, tzinfo=timezone.utc),
    )
    assert decision.action == "start"


def test_decide_schedule_action_stops_outside_window() -> None:
    """Running instances stop outside the window."""
    instance = build_instance(
        "running",
        {
            "thin-controller-timezone": "Australia/Brisbane",
            "thin-controller-on-hours": "09-17",
        },
    )
    decision = decide_schedule_action(
        instance,
        now=datetime(2026, 3, 31, 8, 0, tzinfo=timezone.utc),
    )
    assert decision.action == "stop"


def test_decide_schedule_action_respects_always_on() -> None:
    """Always-on overrides scheduler actions."""
    instance = build_instance(
        "running",
        {
            "thin-controller-timezone": "Australia/Brisbane",
            "thin-controller-on-hours": "09-17",
            "thin-controller-always-on": "true",
        },
    )
    decision = decide_schedule_action(instance)
    assert decision.action is None
    assert decision.reason == "always-on override enabled"


def test_decide_schedule_action_skips_invalid_timezone() -> None:
    """Invalid timezones are logged and skipped."""
    instance = build_instance(
        "running",
        {
            "thin-controller-timezone": "Mars/OlympusMons",
            "thin-controller-on-hours": "09-17",
        },
    )
    decision = decide_schedule_action(instance)
    assert decision.action is None
    assert "invalid timezone" in decision.reason
