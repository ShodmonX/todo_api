from pydantic import BaseModel, ConfigDict

from enum import Enum
from datetime import datetime, date


class StatusEnum(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"    

class TaskBulkUpdateStatus(BaseModel):
    ids: list[int]
    status: StatusEnum
class TaskIn(BaseModel):
    title: str
    description: str | None = None
    priority: PriorityEnum
    due_date: date
    estimated_time: int | None = None
    category_id: int | None = None

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
    category_id: int | None
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

class TaskOutBulkResponse(BaseModel):
    status: str
    message: str
    tasks: list[TaskOut]
