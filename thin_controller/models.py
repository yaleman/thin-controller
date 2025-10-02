"""Models for parsing things"""

from typing import Dict, List, Optional
from pydantic import AliasPath, BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

import boto3


class AWSInstance(BaseModel):
    """AWS Instance model"""

    instance_id: str = Field(..., validation_alias="InstanceId")
    state: str = Field(..., validation_alias=AliasPath("State", "Name"))
    instance_type: str = Field(..., validation_alias="InstanceType")

    tags: Dict[str, str] = Field(..., validation_alias="Tags")
    region: str = Field(..., validation_alias="Placement")

    name: Optional[str] = None

    cron_start: Optional[str] = None
    cron_stop: Optional[str] = None

    @field_validator("region", mode="before")
    @classmethod
    def pull_region(cls, v: Dict[str, str]) -> str:
        """pull the region from the placement dict"""
        return v["AvailabilityZone"][:-1]

    @field_validator("tags", mode="before")
    @classmethod
    def input_to_output(cls, v: List[Dict[str, str]]) -> Dict[str, str]:
        """convert list of dicts to dict"""
        res = {}
        for element in v:
            res[element["Key"]] = element["Value"]
        return res

    @model_validator(mode="after")
    def try_to_get_name(self) -> Self:
        """try to get the name from tags"""
        self.name = self.tags.get("Name")  # pylint: disable=E1101,no-member
        return self


class Config(BaseSettings):
    """Configuration model"""

    regions: str = Field(
        default_factory=lambda: ",".join(
            boto3.session.Session().get_available_regions("ec2")
        ),
    )
    model_config = SettingsConfigDict(env_prefix="THIN_CONTROLLER_")

    def region_list(self) -> List[str]:
        """get the list of regions"""
        return [region.strip() for region in self.regions.split(",")]  # pylint: disable=E1101,no-member
