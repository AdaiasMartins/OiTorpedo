from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .evolution_client import EvolutionClient
from .tasks import send_bulk_messages

app = FastAPI(title="Evolution POC API")


class InstanceCreateRequest(BaseModel):
    instance: str = Field(..., examples=["main"])
    qrcode: bool = True


class QrCodeRequest(BaseModel):
    instance: str = Field(..., examples=["main"])
    output_path: str = "/workspace/qrcode.png"


class SendTextRequest(BaseModel):
    instance: str = Field(..., examples=["main"])
    number: str = Field(..., examples=["5585999999999"])
    text: str = Field(..., examples=["Teste da Evolution API"])


class BulkSendRequest(BaseModel):
    instance: str = Field(..., examples=["main"])
    recipients: list[str] = Field(..., examples=[["5585999999999", "5585888888888"]])
    message: str = Field(..., examples=["Teste em lote via Celery"])
    delay_seconds: float | None = Field(default=None, ge=0)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/instances")
def create_instance(payload: InstanceCreateRequest) -> dict[str, Any]:
    return call_evolution(lambda client: client.create_instance(payload.instance, payload.qrcode))


@app.post("/instances/qrcode")
def qrcode(payload: QrCodeRequest) -> dict[str, Any]:
    return call_evolution(lambda client: client.save_qrcode(payload.instance, payload.output_path))


@app.post("/messages/text")
def send_text(payload: SendTextRequest) -> dict[str, Any]:
    return call_evolution(lambda client: client.send_text(payload.instance, payload.number, payload.text))


@app.post("/messages/bulk")
def send_bulk(payload: BulkSendRequest) -> dict[str, str]:
    task = send_bulk_messages.delay(
        instance=payload.instance,
        recipients=payload.recipients,
        message=payload.message,
        delay_seconds=payload.delay_seconds,
    )
    return {"task_id": task.id}


def call_evolution(operation: Any) -> dict[str, Any]:
    try:
        return operation(EvolutionClient())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
