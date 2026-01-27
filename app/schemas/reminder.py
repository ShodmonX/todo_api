from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime


class ReminderCreate(BaseModel):
    reminder_time: datetime
    task_id: int | None = None

    @field_validator('reminder_time')
    @classmethod
    def validate_reminder_time(cls, v: datetime) -> datetime:
        if not isinstance(v, datetime):
            raise ValueError('reminder_time must be a valid datetime')
        # Convert timezone-aware to naive UTC
        if v.tzinfo is not None:
            v = v.replace(tzinfo=None)
        return v

    model_config = ConfigDict(from_attributes=True)


class ReminderUpdate(BaseModel):
    reminder_time: datetime | None = None
    is_sent: bool | None = None

    @field_validator('reminder_time')
    @classmethod
    def validate_reminder_time(cls, v: datetime | None) -> datetime | None:
        if v is not None and not isinstance(v, datetime):
            raise ValueError('reminder_time must be a valid datetime')
        # Convert timezone-aware to naive UTC
        if v is not None and v.tzinfo is not None:
            v = v.replace(tzinfo=None)
        return v

    model_config = ConfigDict(from_attributes=True)


class TaskReminderCreate(BaseModel):
    reminder_time: datetime

    @field_validator('reminder_time')
    @classmethod
    def validate_reminder_time(cls, v: datetime) -> datetime:
        if not isinstance(v, datetime):
            raise ValueError('reminder_time must be a valid datetime')
        # Convert timezone-aware to naive UTC
        if v.tzinfo is not None:
            v = v.replace(tzinfo=None)
        return v

    model_config = ConfigDict(from_attributes=True)


class ReminderOut(BaseModel):
    id: int
    task_id: int | None
    reminder_time: datetime
    is_sent: bool
    sent_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
