from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import qrcode
import requests

from .config import EVOLUTION_API_KEY, EVOLUTION_BASE_URL, HTTP_TIMEOUT_SECONDS


class EvolutionClient:
    def __init__(
        self,
        base_url: str = EVOLUTION_BASE_URL,
        api_key: str = EVOLUTION_API_KEY,
        timeout: float = HTTP_TIMEOUT_SECONDS,
    ) -> None:
        if not api_key:
            raise ValueError("Configure AUTHENTICATION_API_KEY ou EVOLUTION_API_KEY.")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "apikey": api_key,
                "Content-Type": "application/json",
            }
        )

    def create_instance(self, instance: str, qrcode_enabled: bool = True) -> dict[str, Any]:
        payload = {
            "instanceName": instance,
            "integration": "WHATSAPP-BAILEYS",
            "qrcode": qrcode_enabled,
        }
        return self._request("POST", "/instance/create", json=payload)

    def connect_instance(self, instance: str) -> dict[str, Any]:
        return self._request("GET", f"/instance/connect/{instance}")

    def save_qrcode(self, instance: str, output_path: str = "qrcode.png") -> dict[str, Any]:
        data = self.connect_instance(instance)
        qr_value = self._find_qr_value(data)
        if not qr_value:
            raise ValueError(f"Resposta sem QR Code: {data}")

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        base64_payload = self._extract_base64_payload(qr_value)
        if base64_payload:
            path.write_bytes(base64.b64decode(base64_payload))
        else:
            image = qrcode.make(qr_value)
            image.save(path)

        return {"path": str(path), "response": data}

    def send_text(self, instance: str, number: str, text: str, delay_ms: int = 0) -> dict[str, Any]:
        payload = {
            "number": number,
            "text": text,
        }
        if delay_ms > 0:
            payload["delay"] = delay_ms

        return self._request("POST", f"/message/sendText/{instance}", json=payload)

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        response = self.session.request(
            method,
            f"{self.base_url}{path}",
            timeout=self.timeout,
            **kwargs,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(
                f"Evolution API error {response.status_code} em {path}: {response.text}"
            ) from exc

        if not response.content:
            return {}
        return response.json()

    def _find_qr_value(self, data: dict[str, Any]) -> str | None:
        candidates = [
            data.get("base64"),
            data.get("qrcode"),
            data.get("qrCode"),
            data.get("code"),
        ]

        nested_qrcode = data.get("qrcode")
        if isinstance(nested_qrcode, dict):
            candidates.extend(
                [
                    nested_qrcode.get("base64"),
                    nested_qrcode.get("code"),
                    nested_qrcode.get("qrCode"),
                ]
            )

        for candidate in candidates:
            if isinstance(candidate, str) and candidate.strip():
                return candidate
        return None

    def _extract_base64_payload(self, value: str) -> str | None:
        if value.startswith("data:image"):
            return value.split(",", 1)[1]

        compact = value.strip()
        if len(compact) > 100 and not compact.startswith("2@"):
            return compact

        return None
