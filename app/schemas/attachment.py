from pydantic import BaseModel, ConfigDict

from enum import Enum
from datetime import datetime


class MimeTypeEnum(str, Enum):
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    IMAGE_WEBP = "image/webp"
    APPLICATION_PDF = "application/pdf"
    TEXT_PLAIN = "text/plain"


class AttachmentOut(BaseModel):
    id: int
    filename: str
    file_path: str
    file_size: int
    mime_type: MimeTypeEnum
    task_id: int
    user_id: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)