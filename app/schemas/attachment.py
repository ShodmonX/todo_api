from enum import Enum


class MimeTypeEnum(str, Enum):
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    IMAGE_WEBP = "image/webp"
    APPLICATION_PDF = "application/pdf"
    TEXT_PLAIN = "text/plain"