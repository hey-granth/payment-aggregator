from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


# Provider config schemas


class ProviderConfigBase(BaseModel):
    provider_name: str
    is_primary: bool = False
    priority: int = 0  # lower number means higher priority


class ProviderConfigCreate(ProviderConfigBase):
    credentials: dict


class ProviderConfig(ProviderConfigBase):
    id: UUID
    project_id: UUID

    class Config:
        from_attributes = True


# Project schemas


class ProjectBase(BaseModel):
    project_name: str
    project_id: UUID
    created_at: datetime
    updated_at: datetime


# doesn't need any extra fields, so we can just inherit from ProjectBase
class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    api_key: str
    provider_config: list[ProviderConfig] = []

    class Config:
        from_attributes = True
