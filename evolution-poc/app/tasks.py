from __future__ import annotations

import json
import logging
from typing import Any

from .celery_app import celery_app
from .config import SEND_DELAY_SECONDS
from .evolution_client import EvolutionClient

logger = logging.getLogger(__name__)


def log_event(event: str, **fields: Any) -> None:
    logger.info(json.dumps({"event": event, **fields}, ensure_ascii=True))


@celery_app.task(
    bind=True,
    name="send_single_message",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
    soft_time_limit=45,
    time_limit=60,
    acks_late=True,
    reject_on_worker_lost=True,
)
def send_single_message(
    self: Any,
    instance: str,
    number: str,
    message: str,
) -> dict[str, Any]:
    try:
        response = EvolutionClient().send_text(instance=instance, number=number, text=message)
        result = {"instance": instance, "number": number, "status": "success", "response": response}
        log_event("message_sent", task_id=self.request.id, **result)
        return result
    except Exception as exc:
        log_event(
            "message_failed",
            task_id=self.request.id,
            instance=instance,
            number=number,
            status="error",
            retry=self.request.retries,
            error=str(exc),
        )
        raise


def enqueue_bulk_messages(
    instance: str,
    recipients: list[str],
    message: str,
    delay_seconds: float | None = None,
) -> dict[str, Any]:
    delay = SEND_DELAY_SECONDS if delay_seconds is None else max(delay_seconds, 0)
    task_ids: list[str] = []

    for index, number in enumerate(recipients):
        task = send_single_message.apply_async(
            kwargs={"instance": instance, "number": number, "message": message},
            countdown=index * delay,
        )
        task_ids.append(task.id)

    result = {
        "instance": instance,
        "total": len(recipients),
        "delay_seconds": delay,
        "task_ids": task_ids,
    }
    log_event("bulk_enqueued", **result)
    return result


@celery_app.task(name="send_bulk_messages")
def send_bulk_messages(
    instance: str,
    recipients: list[str],
    message: str,
    delay_seconds: float | None = None,
) -> dict[str, Any]:
    return enqueue_bulk_messages(
        instance=instance,
        recipients=recipients,
        message=message,
        delay_seconds=delay_seconds,
    )
