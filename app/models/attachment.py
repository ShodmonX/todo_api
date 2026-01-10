from sqlalchemy import Integer, String, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Any

from app.database import Base
from app.schemas import MimeTypeEnum


class Attachment(Base):
    __tablename__ = "attachments"

    id:         Mapped[int]             = mapped_column(Integer, primary_key=True)
    filename:   Mapped[str]             = mapped_column(String(255), nullable=False)
    file_path:  Mapped[str]             = mapped_column(String(500), nullable=False, unique=True)
    file_size:  Mapped[int]             = mapped_column(Integer, nullable=False)
    mime_type:  Mapped[MimeTypeEnum]    = mapped_column(Enum(MimeTypeEnum, name="mime_type_enum"), nullable=False)
    task_id:    Mapped[int]             = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id:    Mapped[int]             = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_at:    Mapped[datetime]        = mapped_column(DateTime, server_default=func.now(), default=func.now())

    task: Mapped["Task"] = relationship(back_populates="attachments")  # type: ignore
    user: Mapped["User"] = relationship(back_populates="attachments")  # type: ignore

    def __repr__(self) -> str:
        return f"<Attachment {self.filename} (id={self.id})>"

    def __str__(self) -> str:
        return self.filename

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "mime_type": self.mime_type.value,
            "task_id": self.task_id,
            "user_id": self.user_id,
            "uploaded_at": self.uploaded_at,
        }

