from __future__ import annotations

from celery import Celery

from .config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    "evolution_poc",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Fortaleza",
    enable_utc=True,
)
