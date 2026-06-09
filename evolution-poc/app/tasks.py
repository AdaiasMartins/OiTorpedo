from __future__ import annotations

import json
import logging
import time
from typing import Any

from .celery_app import celery_app
from .config import SEND_DELAY_SECONDS
from .evolution_client import EvolutionClient

logger = logging.getLogger(__name__)


def log_event(event: str, **fields: Any) -> None:
    logger.info(json.dumps({"event": event, **fields}, ensure_ascii=True))


@celery_app.task(name="send_bulk_messages")
def send_bulk_messages(
    instance: str,
    recipients: list[str],
    message: str,
    delay_seconds: float | None = None,
) -> dict[str, Any]:
    delay = SEND_DELAY_SECONDS if delay_seconds is None else delay_seconds
    client = EvolutionClient()
    successes: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for index, number in enumerate(recipients):
        try:
            response = client.send_text(instance=instance, number=number, text=message)
            successes.append({"number": number, "response": response})
            log_event("message_sent", instance=instance, number=number, status="success")
        except Exception as exc:
            failures.append({"number": number, "error": str(exc)})
            log_event("message_failed", instance=instance, number=number, status="error", error=str(exc))

        if index < len(recipients) - 1 and delay > 0:
            time.sleep(delay)

    result = {
        "instance": instance,
        "total": len(recipients),
        "success_count": len(successes),
        "failure_count": len(failures),
        "successes": successes,
        "failures": failures,
    }
    log_event("bulk_finished", **result)
    return result
