"""test model parsing"""

from thin_controller.models import AWSInstance


TEST_INPUT = {
    "Reservations": [
        {
            "Groups": [],
            "Instances": [
                {
                    "AmiLaunchIndex": 0,
                    "ImageId": "ami-aaaabbbbffffccccc",
                    "InstanceId": "i-0b12345042be12345",
                    "InstanceType": "c7a.medium",
                    "KeyName": "2023-09-20-asdfasdf",
                    "LaunchTime": "2024-04-12 23:46:26+00:00",
                    "Monitoring": {"State": "disabled"},
                    "Placement": {
                        "AvailabilityZone": "us-east-1a",
                        "GroupName": "",
                        "Tenancy": "default",
                    },
                    "PrivateDnsName": "ip-10-0-0-22.ec2.internal",
                    "PrivateIpAddress": "10.0.0.22",
                    "ProductCodes": [],
                    "PublicDnsName": "",
                    "State": {"Code": 80, "Name": "stopped"},
                    "StateTransitionReason": "User initiated (2024-04-15 03:32:59 GMT)",
                    "SubnetId": "subnet-00a3aaaabbbbccccc",
                    "VpcId": "vpc-0c19bb7876aaaffff",
                    "Architecture": "x86_64",
                    "BlockDeviceMappings": [
                        {
                            "DeviceName": "/dev/xvda",
                            "Ebs": {
                                "AttachTime": "2024-01-03 05:22:39+00:00",
                                "DeleteOnTermination": False,
                                "Status": "attached",
                                "VolumeId": "vol-000000b0f59e651d8",
                            },
                        }
                    ],
                    "ClientToken": "f99cda1d-a31d-4901-b16d-e13779ffe67e",
                    "EbsOptimized": True,
                    "EnaSupport": True,
                    "Hypervisor": "xen",
                    "IamInstanceProfile": {
                        "Arn": "arn:aws:iam::1234567890:instance-profile/MagicalFairyLand",
                        "Id": "AIPAZZZZTTTTSL7IZRXJ2",
                    },
                    "NetworkInterfaces": [
                        {
                            "Attachment": {
                                "AttachTime": "2023-09-20 01:16:01+00:00",
                                "AttachmentId": "eni-attach-0a5feaa70f30f9bf7",
                                "DeleteOnTermination": True,
                                "DeviceIndex": 0,
                                "Status": "attached",
                                "NetworkCardIndex": 0,
                            },
                            "Description": "",
                            "Groups": [
                                {
                                    "GroupName": "foobar-pwny-land",
                                    "GroupId": "sg-0cc5a799337d08c78",
                                },
                                {
                                    "GroupName": "party-ssh",
                                    "GroupId": "sg-000db6e103626676e",
                                },
                                {
                                    "GroupName": "party-pwny-land",
                                    "GroupId": "sg-0ba353de19df1dbfe",
                                },
                            ],
                            "Ipv6Addresses": [],
                            "MacAddress": "0a:ce:ff:11:cc:ff",
                            "NetworkInterfaceId": "eni-068e656371749a514",
                            "OwnerId": "1234567890",
                            "PrivateDnsName": "ip-10-0-0-22.ec2.internal",
                            "PrivateIpAddress": "10.0.0.22",
                            "PrivateIpAddresses": [
                                {
                                    "Primary": True,
                                    "PrivateDnsName": "ip-10-0-0-22.ec2.internal",
                                    "PrivateIpAddress": "10.0.0.22",
                                }
                            ],
                            "SourceDestCheck": True,
                            "Status": "in-use",
                            "SubnetId": "subnet-00a3b9931bd173fc3",
                            "VpcId": "vpc-0c19bb78762a1aec0",
                            "InterfaceType": "interface",
                        }
                    ],
                    "RootDeviceName": "/dev/xvda",
                    "RootDeviceType": "ebs",
                    "SecurityGroups": [
                        {
                            "GroupName": "foobar-pwny-land",
                            "GroupId": "sg-0cc5a799337d08c78",
                        },
                        {"GroupName": "party-ssh", "GroupId": "sg-000db6e103626676e"},
                        {
                            "GroupName": "party-mltk-pwny-land",
                            "GroupId": "sg-0ba353de19df1dbfe",
                        },
                    ],
                    "SourceDestCheck": True,
                    "StateReason": {
                        "Code": "Client.UserInitiatedShutdown",
                        "Message": "Client.UserInitiatedShutdown: User initiated shutdown",
                    },
                    "Tags": [
                        {"Key": "Name", "Value": "party-ai-cheese"},
                    ],
                    "VirtualizationType": "hvm",
                    "CpuOptions": {"CoreCount": 1, "ThreadsPerCore": 1},
                    "CapacityReservationSpecification": {
                        "CapacityReservationPreference": "open"
                    },
                    "HibernationOptions": {"Configured": False},
                    "MetadataOptions": {
                        "State": "applied",
                        "HttpTokens": "required",
                        "HttpPutResponseHopLimit": 2,
                        "HttpEndpoint": "enabled",
                        "HttpProtocolIpv6": "disabled",
                        "InstanceMetadataTags": "disabled",
                    },
                    "EnclaveOptions": {"Enabled": False},
                    "BootMode": "uefi-preferred",
                    "PlatformDetails": "Linux/UNIX",
                    "UsageOperation": "RunInstances",
                    "UsageOperationUpdateTime": "2023-09-20 01:16:01+00:00",
                    "PrivateDnsNameOptions": {
                        "HostnameType": "ip-name",
                        "EnableResourceNameDnsARecord": True,
                        "EnableResourceNameDnsAAAARecord": False,
                    },
                    "MaintenanceOptions": {"AutoRecovery": "default"},
                    "CurrentInstanceBootMode": "uefi",
                }
            ],
            "OwnerId": "1234567890",
            "ReservationId": "r-090260d8c057c6a4e",
        },
    ]
}


def test_parse_describe() -> None:
    """test parsing of the describe output"""
    instances = []
    for reservation in TEST_INPUT.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            parsed = AWSInstance.model_validate(instance)
            instances.append(parsed)

    assert len(instances) == 1
    assert instances[0].instance_id == "i-0b12345042be12345"
    assert instances[0].state == "stopped"
    assert instances[0].region == "us-east-1"
