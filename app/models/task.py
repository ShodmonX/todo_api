from sqlalchemy import Integer, String, Text, text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime

from app.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id:                 Mapped[int]         = mapped_column(Integer, primary_key=True)
    title:              Mapped[str]         = mapped_column(String(255))
    description:        Mapped[str | None]         = mapped_column(Text, nullable=True)
    status:             Mapped[str]         = mapped_column(String(25), default="pending", server_default=text("'pending'"))
    priority:           Mapped[str]         = mapped_column(String(25), default="low", server_default=text("'low'"))
    due_date:           Mapped[datetime]    = mapped_column(DateTime)
    completed_at:       Mapped[datetime | None]    = mapped_column(DateTime, nullable=True)
    user_id:            Mapped[int]         = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    # category_id: UUID (FK to Category, nullable)
    created_at:         Mapped[datetime]    = mapped_column(DateTime, default=func.now(), server_default=func.now())
    updated_at:         Mapped[datetime]    = mapped_column(DateTime, default=func.now(), server_default=func.now())
    estimated_time:     Mapped[int | None]         = mapped_column(Integer, nullable=True)
    actual_time:        Mapped[int | None]         = mapped_column(Integer, nullable=True)

    user:               Mapped["User"]      = relationship(back_populates="tasks") # type: ignore
