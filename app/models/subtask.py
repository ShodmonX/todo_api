from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Any

from app.database import Base


class Subtask(Base):
    __tablename__ = "subtasks"

    id:             Mapped[int]             = mapped_column(Integer, primary_key=True)
    title:          Mapped[str]             = mapped_column(String(255), nullable=False)
    is_completed:   Mapped[bool]            = mapped_column(Boolean, default=False, server_default='false', nullable=False)
    task_id:        Mapped[int]             = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at:     Mapped[datetime]        = mapped_column(DateTime, default=func.now(), server_default=func.now())
    completed_at:   Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    task: Mapped["Task"] = relationship(back_populates="subtasks")  # type: ignore

    def __repr__(self) -> str:
        return f"<Subtask {self.title} (id={self.id})>"

    def __str__(self) -> str:
        return self.title

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "is_completed": self.is_completed,
            "task_id": self.task_id,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }
