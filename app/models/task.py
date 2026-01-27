from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Any

from app.database import Base
from app.schemas import StatusEnum, PriorityEnum


class Task(Base):
    __tablename__ = "tasks"

    id:                 Mapped[int]         = mapped_column(Integer, primary_key=True)
    title:              Mapped[str]         = mapped_column(String(255))
    description:        Mapped[str | None]         = mapped_column(Text, nullable=True)
    status:             Mapped[StatusEnum]         = mapped_column(Enum(StatusEnum, name="task_status"), default=StatusEnum.pending, server_default=StatusEnum.pending)
    priority:           Mapped[PriorityEnum]         = mapped_column(Enum(PriorityEnum, name="tasks_priority"), default=PriorityEnum.low, server_default=PriorityEnum.low)
    due_date:           Mapped[datetime | None]    = mapped_column(DateTime, nullable=True)
    completed_at:       Mapped[datetime | None]    = mapped_column(DateTime, nullable=True)
    user_id:            Mapped[int]         = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    category_id:        Mapped[int]         = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    created_at:         Mapped[datetime]    = mapped_column(DateTime, default=func.now(), server_default=func.now())
    updated_at:         Mapped[datetime]    = mapped_column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now())
    estimated_time:     Mapped[int | None]         = mapped_column(Integer, nullable=True)
    actual_time:        Mapped[int | None]         = mapped_column(Integer, nullable=True)

    user:               Mapped["User"]      = relationship(back_populates="tasks") # type: ignore
    category:           Mapped["Category"]  = relationship(back_populates="tasks", passive_deletes=True) # type: ignore
    attachments:        Mapped[list["Attachment"]] = relationship(back_populates="task", cascade="all, delete-orphan") # type: ignore 
    subtasks:           Mapped[list["Subtask"]] = relationship(back_populates="task", cascade="all, delete-orphan") # type: ignore

    def __repr__(self):
        return f"<User {self.title} (id={self.id})>"

    def __str__(self):
        return f"<User {self.title}>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date,
            "completed_at": self.completed_at,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "estimated_time": self.estimated_time,
            "actual_time": self.actual_time,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

