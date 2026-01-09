from pydantic import BaseModel, ConfigDict, Field


class CategoryOut(BaseModel):
    id: int
    name: str
    color: str
    icon: str | None

    model_config = ConfigDict(from_attributes=True)

class CategoryIn(BaseModel):
    name: str = Field(..., min_length=3, max_length=55)
    color: str = Field(..., min_length=7, max_length=7, pattern=r'^#[a-f0-9]{6}$')

class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=55)
    color: str | None = Field(None, min_length=7, max_length=7, pattern=r'^#[a-f0-9]{6}$')