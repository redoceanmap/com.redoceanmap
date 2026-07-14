"""webhook_token.py — /automation/* 라우터 공용 웹훅 토큰 검증 의존성.

외부 자동화(n8n·cron)는 X-Webhook-Token 헤더로 호출자를 검증한다
(N8N_INBOUND_TOKEN env, 비면 검증 생략 — 로컬 개발).
"""
from __future__ import annotations

from fastapi import Header, HTTPException

from core.config import N8N_INBOUND_TOKEN


def verify_webhook_token(
    x_webhook_token: str | None = Header(default=None, alias="X-Webhook-Token"),
) -> None:
    if N8N_INBOUND_TOKEN and x_webhook_token != N8N_INBOUND_TOKEN:
        raise HTTPException(status_code=401, detail="웹훅 토큰이 올바르지 않습니다.")
