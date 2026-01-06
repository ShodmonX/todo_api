from celery import Task # pyright: ignore[reportMissingTypeStubs]

from typing import Any

from app.core import celery_app
from app.utils import send_verification_email


class BaseTaskWithRetry(Task):
    autoretry_for = (Exception,)
    max_retries = 3
    retry_backoff = True
    retry_backoff_max = 700
    retry_jitter = True

@celery_app.task(bind=True) # pyright: ignore[reportUntypedFunctionDecorator, reportUnknownMemberType]
def send_verify_email_task(self: Any, email: str, verification_url: str):
    send_verification_email(email, verification_url)
    return f"Tasdiqlash emaili jo'natildi: {email}"