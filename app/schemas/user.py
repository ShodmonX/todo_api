from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from datetime import datetime


class UserIn(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "name@example.com"})
    username: str
    password: str = Field(..., min_length=8, max_length=72)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("email", mode="before")
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip().lower()

class UserLogIn(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "name@example.com"})
    password: str = Field(..., min_length=8, max_length=72)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("email", mode="before")
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip().lower()

class UserOut(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "name@example.com"})
    username: str
    timezone: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)