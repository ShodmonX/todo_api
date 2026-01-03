from pydantic import BaseModel, ConfigDict

from enum import Enum
from datetime import datetime


class StatusEnum(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"    

class TaskIn(BaseModel):
    title: str
    description: str | None = None
    priority: PriorityEnum
    due_date: datetime
    estimated_time: int | None = None

    model_config = ConfigDict(from_attributes=True)

class TaskOut(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: StatusEnum
    priority: PriorityEnum
    due_date: datetime
    completed_at: datetime | None = None
    user_id: int
    created_at: datetime
    updated_at: datetime
    estimated_time: int | None = None
    actual_time: int | None = None

    model_config = ConfigDict(from_attributes=True)

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    completed_at: datetime | None = None
    estimated_time: int | None = None
    actual_time: int | None = None

class TaskOutResponse(BaseModel):
    status: str
    message: str
    task: TaskOut
