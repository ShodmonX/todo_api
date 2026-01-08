from sqlalchemy import Integer, String, ForeignKey, DateTime, UniqueConstraint, text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Any

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id:             Mapped[int]         = mapped_column(Integer, primary_key=True)
    name:           Mapped[str]         = mapped_column(String(55), index=True, nullable=False)
    color:          Mapped[str]         = mapped_column(String(7), default="#6B7280", server_default=text("'#6B7280'"), nullable=False)
    icon:           Mapped[str]         = mapped_column(String(255), nullable=True)
    user_id:        Mapped[int]         = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at:     Mapped[datetime]    = mapped_column(DateTime, default=func.now(), server_default=func.now())

    tasks: Mapped[list['Task']] = relationship(back_populates="category", passive_deletes=True) # type: ignore
    user: Mapped['User'] = relationship(back_populates="categories") # type: ignore

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_categories_user_name"),
    )

    def __repr__(self):
        return f"<Category {self.name} (id={self.id})>"

    def __str__(self):
        return f"<Category {self.name}>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "icon": self.icon,
            "user_id": self.user_id,
            "created_at": self.created_at
        }


