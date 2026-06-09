from __future__ import annotations

import os


def env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


EVOLUTION_BASE_URL = env("EVOLUTION_BASE_URL", env("SERVER_URL", "http://localhost:8080")).rstrip("/")
EVOLUTION_API_KEY = env("EVOLUTION_API_KEY", env("AUTHENTICATION_API_KEY", ""))

CELERY_BROKER_URL = env("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

SEND_DELAY_SECONDS = float(env("SEND_DELAY_SECONDS", "3"))
HTTP_TIMEOUT_SECONDS = float(env("HTTP_TIMEOUT_SECONDS", "30"))
