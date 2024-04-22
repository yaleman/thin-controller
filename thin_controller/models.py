from typing import Dict, List, Optional
from pydantic import AliasPath, BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

import boto3


class AWSInstance(BaseModel):
    id: str = Field(validation_alias="InstanceId")
    state: str = Field(validation_alias=AliasPath("State", "Name"))
    instance_type: str = Field(validation_alias="InstanceType")

    tags: Dict[str, str] = Field(validation_alias="Tags")
    region: str = Field(validation_alias="Placement")

    name: Optional[str] = None

    cron_start: Optional[str] = None
    cron_stop: Optional[str] = None

    @field_validator("region", mode="before")
    @classmethod
    def pull_region(cls, v: Dict[str, str]) -> str:
        return v["AvailabilityZone"][:-1]

    @field_validator("tags", mode="before")
    @classmethod
    def input_to_output(cls, v: List[Dict[str, str]]) -> Dict[str, str]:
        res = {}
        for element in v:
            res[element["Key"]] = element["Value"]
        return res

    @model_validator(mode="after")
    def try_to_get_name(self) -> Self:
        self.name = self.tags.get("Name")
        return self


class Config(BaseSettings):
    regions: str = ",".join(boto3.session.Session().get_available_regions("ec2"))
    model_config = SettingsConfigDict(env_prefix="THIN_CONTROLLER_")

    def region_list(self) -> List[str]:
        """get the list of regions"""
        return [region.strip() for region in self.regions.split(",")]
