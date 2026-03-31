"""Tests for shared EC2 helpers."""

from thin_controller.ec2 import list_managed_instances


def build_instance(instance_id: str) -> dict[str, object]:
    """Build a small EC2 instance payload for tests."""
    return {
        "InstanceId": instance_id,
        "State": {"Name": "running"},
        "InstanceType": "t3.micro",
        "Tags": [{"Key": "Name", "Value": f"instance-{instance_id}"}],
        "Placement": {"AvailabilityZone": "ap-southeast-2a"},
    }


def test_list_managed_instances_reads_all_pages(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Managed instances are collected across paginated AWS responses."""

    class FakePaginator:
        """Simple paginator double for describe_instances."""

        def paginate(self, Filters: list[dict[str, object]]) -> list[dict[str, object]]:
            assert Filters == [
                {"Name": "tag:thin_controller_managed", "Values": ["true"]}
            ]
            return [
                {"Reservations": [{"Instances": [build_instance("i-0b12345042be12345")]}]},
                {"Reservations": [{"Instances": [build_instance("i-0b12345042be12346")]}]},
            ]

    class FakeClient:
        """Return a paginator for describe_instances."""

        def get_paginator(self, operation_name: str) -> FakePaginator:
            assert operation_name == "describe_instances"
            return FakePaginator()

    class FakeSession:
        """Return a fake EC2 client for the requested region."""

        def __init__(self, region_name: str) -> None:
            assert region_name == "ap-southeast-2"

        def client(self, service_name: str) -> FakeClient:
            assert service_name == "ec2"
            return FakeClient()

    monkeypatch.setattr("thin_controller.ec2.Session", FakeSession)

    instances = list_managed_instances(["ap-southeast-2"])

    assert [instance.instance_id for instance in instances] == [
        "i-0b12345042be12345",
        "i-0b12345042be12346",
    ]
