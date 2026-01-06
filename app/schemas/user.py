from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from datetime import datetime

from app.utils import check_domain


class UserIn(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "name@example.com"})
    username: str = Field(..., min_length=5, max_length=25)
    password: str = Field(..., min_length=8, max_length=72)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return value
        
        value = value.strip().lower()

        if not check_domain(value):
            raise ValueError("Email domain is not valid")

        return value
    
    @field_validator("username", mode="before")
    @classmethod
    def validate_username(cls, value: str | None) -> str | None:
        if value is None:
            return value
        
        value = value.strip()

        import re
        pattern = r"^[A-Za-z][A-Za-z0-9_]*$"
        if not re.fullmatch(pattern, value):
            raise ValueError(
                "Username faqat harf, raqam va '_' dan iborat bo‘lishi, "
                "hamda harf bilan boshlanishi kerak"
            )

        return value


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

class UserOutResponse(BaseModel):
    status: str
    message: str
    user: UserOut

class UserUpdate(BaseModel):
    username: str | None = None
    timezone: str | None = None

class UserChangePassword(BaseModel):
    old_password: str = Field(..., min_length=8, max_length=72)
    new_password: str = Field(..., min_length=8, max_length=72)

class UserNewPassword(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=72)