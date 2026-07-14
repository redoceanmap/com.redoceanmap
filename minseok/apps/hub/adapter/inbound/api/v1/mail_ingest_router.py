"""mail_ingest_router.py — 외부 자동화(n8n)의 수신 메일 저장 창구."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from hub.adapter.inbound.api.schemas.mail_ingest_schema import (
    InboundMailResult,
    InboundMailSchema,
)
from hub.adapter.inbound.api.v1.webhook_token import verify_webhook_token
from hub.app.dtos.inbound_mail_dto import InboundMailItem
from hub.app.ports.input.mail_ingest_use_case import MailIngestUseCase
from hub.dependencies.mail_ingest_provider import get_mail_ingest_use_case

mail_ingest_router = APIRouter(
    prefix="/automation", tags=["automation"],
    dependencies=[Depends(verify_webhook_token)],
)


@mail_ingest_router.post("/mail", response_model=InboundMailResult, summary="n8n 수신 메일 저장")
async def ingest_mail(
    payload: InboundMailSchema,
    use_case: MailIngestUseCase = Depends(get_mail_ingest_use_case),
) -> InboundMailResult:
    saved = await use_case.receive(InboundMailItem(
        message_id=payload.messageId,
        subject=payload.subject,
        sender=payload.sender,
        recipient=payload.recipient,
        preview=payload.preview,
    ))
    return InboundMailResult(saved=saved, messageId=payload.messageId)
