from celery import Celery # pyright: ignore[reportMissingTypeStubs]

from app.config import settings


celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.email"]
)

celery_app.conf.update( # type: ignore
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tashkent",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
)