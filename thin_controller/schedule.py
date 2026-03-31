"""Schedule parsing and evaluation for managed EC2 instances."""

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from thin_controller.models import AWSInstance

ALWAYS_ON_TAG = "thin-controller-always-on"
ON_HOURS_TAG = "thin-controller-on-hours"
TIMEZONE_TAG = "thin-controller-timezone"
TRUTHY_VALUES = {"1", "true"}
ON_HOURS_PATTERN = re.compile(r"^\s*(\d{1,2})-(\d{1,2})\s*$")


@dataclass(frozen=True)
class ScheduleDecision:
    """The scheduler decision for a managed instance."""

    action: str | None
    reason: str


def is_always_on(tag_value: str | None) -> bool:
    """Return True when the always-on tag disables scheduling."""
    if tag_value is None:
        return False
    return tag_value.strip().lower() in TRUTHY_VALUES


def parse_on_hours(tag_value: str) -> tuple[int, int]:
    """Parse a schedule window in HH-HH format."""
    match = ON_HOURS_PATTERN.match(tag_value)
    if match is None:
        raise ValueError("thin-controller-on-hours must use HH-HH format")

    start_hour = int(match.group(1))
    end_hour = int(match.group(2))
    if start_hour > 23 or end_hour > 23:
        raise ValueError("thin-controller-on-hours must use 0-23 hours")
    if start_hour == end_hour:
        raise ValueError("thin-controller-on-hours start and end cannot match")
    return start_hour, end_hour


def is_hour_in_window(hour: int, start_hour: int, end_hour: int) -> bool:
    """Return True when an hour falls within the configured window."""
    if start_hour < end_hour:
        return start_hour <= hour < end_hour
    return hour >= start_hour or hour < end_hour


def decide_schedule_action(
    instance: AWSInstance,
    now: datetime | None = None,
) -> ScheduleDecision:
    """Decide whether the scheduler should start or stop an instance."""
    if is_always_on(instance.tags.get(ALWAYS_ON_TAG)):
        return ScheduleDecision(action=None, reason="always-on override enabled")

    timezone_name = instance.tags.get(TIMEZONE_TAG)
    on_hours = instance.tags.get(ON_HOURS_TAG)
    if timezone_name is None or on_hours is None:
        return ScheduleDecision(action=None, reason="schedule tags not configured")

    try:
        instance_timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return ScheduleDecision(
            action=None,
            reason=f"invalid timezone tag: {timezone_name}",
        )

    try:
        start_hour, end_hour = parse_on_hours(on_hours)
    except ValueError as error:
        return ScheduleDecision(action=None, reason=str(error))

    current_time = now or datetime.now(timezone.utc)
    local_time = current_time.astimezone(instance_timezone)
    inside_window = is_hour_in_window(local_time.hour, start_hour, end_hour)

    if instance.state == "running" and not inside_window:
        return ScheduleDecision(action="stop", reason="outside scheduled window")
    if instance.state == "stopped" and inside_window:
        return ScheduleDecision(action="start", reason="inside scheduled window")
    if instance.state not in {"running", "stopped"}:
        return ScheduleDecision(
            action=None,
            reason=f"instance state {instance.state} is not scheduler-actionable",
        )
    if inside_window:
        return ScheduleDecision(action=None, reason="already running in window")
    return ScheduleDecision(action=None, reason="already stopped outside window")
