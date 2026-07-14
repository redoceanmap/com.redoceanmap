"""email_request_router.py — 이메일 발송 요청 인바운드 어댑터 (액터: 사용자/프론트)."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from hub.adapter.inbound.api.schemas.email_request_schema import (
    EmailRequestResultSchema,
    EmailRequestSchema,
)
from hub.app.dtos.email_request_dto import EmailRequestCommand
from hub.app.ports.input.email_request_use_case import EmailRequestUseCase
from hub.dependencies.email_request_provider import get_email_request_use_case

logger = logging.getLogger(__name__)

email_request_router = APIRouter(prefix="/email", tags=["hub-email"])


@email_request_router.post("/request", response_model=EmailRequestResultSchema)
async def request_email(
    schema: EmailRequestSchema,
    use_case: EmailRequestUseCase = Depends(get_email_request_use_case),
) -> EmailRequestResultSchema:
    logger.info("[hub/email/request] to=%s", schema.to)
    result = await use_case.request(
        EmailRequestCommand(to_email=schema.to, content=schema.content)
    )
    return EmailRequestResultSchema(status=result.status, detail=result.detail)
