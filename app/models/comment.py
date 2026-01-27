from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Any

from app.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id:             Mapped[int]             = mapped_column(Integer, primary_key=True)
    content:        Mapped[str]             = mapped_column(Text, nullable=False)
    task_id:        Mapped[int]             = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id:        Mapped[int]             = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at:     Mapped[datetime]        = mapped_column(DateTime, default=func.now(), server_default=func.now())
    updated_at:     Mapped[datetime]        = mapped_column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now())

    task: Mapped["Task"] = relationship(back_populates="comments")  # type: ignore
    user: Mapped["User"] = relationship(back_populates="comments")  # type: ignore

    def __repr__(self) -> str:
        return f"<Comment {self.id} on Task {self.task_id}>"

    def __str__(self) -> str:
        return f"Comment by User {self.user_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "task_id": self.task_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
