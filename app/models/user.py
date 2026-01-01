from sqlalchemy import String, Boolean, DateTime, Integer, text, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime, timezone

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id:                 Mapped[int]         = mapped_column(Integer, primary_key=True)
    email:              Mapped[str]         = mapped_column(String(55), unique=True, index=True, nullable=False)
    username:           Mapped[str]         = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password:    Mapped[str]         = mapped_column(String(255), nullable=False)
    is_active:          Mapped[bool]        = mapped_column(Boolean, default=True, server_default=text('true'), nullable=False)
    is_verified:        Mapped[bool]        = mapped_column(Boolean, default=False, server_default=text('false'), nullable=False)
    is_superuser:       Mapped[bool]        = mapped_column(Boolean, default=False, server_default=text('false'), nullable=False)
    created_at:         Mapped[datetime]    = mapped_column(DateTime, default=func.now(), server_default=func.now())
    last_login:         Mapped[datetime]    = mapped_column(DateTime, default=func.now(), server_default=func.now())
    profile_image:      Mapped[str]         = mapped_column(String(255), nullable=True)
    timezone:           Mapped[str]         = mapped_column(String(255), default="Asia/Tashkent", server_default=text("'Asia/Tashkent'"), nullable=True)
    
    __table_args__ = (
        UniqueConstraint("username", name="uq_user_username"),
        UniqueConstraint("email", name="uq_user_email"),
    )

    def __repr__(self):
        return f"<User {self.username}>"

    def __str__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "profile_image": self.profile_image,
            "timezone": self.timezone
        }