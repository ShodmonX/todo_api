from sqlalchemy import Integer, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Any

from app.database import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id:              Mapped[int]              = mapped_column(Integer, primary_key=True)
    task_id:         Mapped[int | None]      = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True, index=True)
    reminder_time:   Mapped[datetime]        = mapped_column(DateTime, nullable=False, index=True)
    is_sent:         Mapped[bool]            = mapped_column(Boolean, default=False, server_default='false', index=True)
    sent_at:         Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at:      Mapped[datetime]        = mapped_column(DateTime, default=func.now(), server_default=func.now())

    task:            Mapped["Task"]          = relationship(back_populates="reminders") # type: ignore

    def __repr__(self):
        return f"<Reminder {self.id} (task_id={self.task_id})>"

    def __str__(self):
        return f"<Reminder {self.id}>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "reminder_time": self.reminder_time,
            "is_sent": self.is_sent,
            "sent_at": self.sent_at,
            "created_at": self.created_at
        }
