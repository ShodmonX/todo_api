from pydantic import BaseModel, ConfigDict, field_validator

from datetime import datetime


class SubtaskCreate(BaseModel):
    title: str
    is_completed: bool = False

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()


class SubtaskUpdate(BaseModel):
    title: str | None = None
    is_completed: bool | None = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is not None and (not v or not v.strip()):
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v


class SubtaskOut(BaseModel):
    id: int
    title: str
    is_completed: bool
    task_id: int
    created_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
