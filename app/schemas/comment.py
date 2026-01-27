from pydantic import BaseModel, ConfigDict, field_validator

from datetime import datetime


class CommentCreate(BaseModel):
    content: str

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()


class CommentUpdate(BaseModel):
    content: str

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()


class CommentOut(BaseModel):
    id: int
    content: str
    task_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
