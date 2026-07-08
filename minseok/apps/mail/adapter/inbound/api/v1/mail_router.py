from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from mail.app.ports.input.inbound_mail_use_case import InboundMailUseCase
from mail.dependencies.mail_provider import get_inbound_mail_use_case
from mail.adapter.inbound.api.schemas.postman_schema import PostmanResponseSchema
from mail.app.dtos.postman_dto import PostmanQuery
from mail.app.ports.input.postman_use_case import PostmanUseCase
from mail.dependencies.postman_provider import get_postman_use_case

mail_router = APIRouter(prefix="/mail", tags=["mail"])


class InboundMailItemSchema(BaseModel):
    id: int
    messageId: str
    subject: str
    sender: str
    recipient: str
    preview: str
    receivedAt: str


def _to_schema(m) -> InboundMailItemSchema:
    return InboundMailItemSchema(
        id=m.id or 0,
        messageId=m.message_id,
        subject=m.subject,
        sender=m.sender,
        recipient=m.recipient,
        preview=m.preview,
        receivedAt=m.received_at.isoformat() if m.received_at else "",
    )


@mail_router.get("/list", response_model=list[InboundMailItemSchema], summary="수신 메일 목록")
async def list_mails(
    use_case: InboundMailUseCase = Depends(get_inbound_mail_use_case),
) -> list[InboundMailItemSchema]:
    return [_to_schema(m) for m in await use_case.list_mails()]


@mail_router.get("/search", response_model=list[InboundMailItemSchema], summary="수신 메일 의미 검색")
async def search_mails(
    q: str,
    limit: int = 5,
    use_case: InboundMailUseCase = Depends(get_inbound_mail_use_case),
) -> list[InboundMailItemSchema]:
    """질의를 bge-m3로 임베딩해 pgvector 코사인 유사도 순으로 반환한다."""
    return [_to_schema(m) for m in await use_case.search_mails(q, limit)]


@mail_router.get("/myself", response_model=PostmanResponseSchema)
async def introduce_myself(
    postman: PostmanUseCase = Depends(get_postman_use_case)
) -> PostmanResponseSchema:
    result = await postman.introduce_myself(
        PostmanQuery(
            id=8,
            name="수신 메일함 (mail)"
        )
    )
    return PostmanResponseSchema(
        id=result.id, name=result.name, introduction=result.introduction
    )
