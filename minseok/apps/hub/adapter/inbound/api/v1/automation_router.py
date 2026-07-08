"""automation_router.py — 외부 자동화(n8n)의 단일 인바운드 창구.

ragwatson star_craft 패턴: 자동화는 허브만 알고, 허브 유스케이스가 스포크 구현
(포트 주입)에 위임한다. X-Webhook-Token 헤더로 호출자를 검증한다.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException

from core.config import N8N_INBOUND_TOKEN
from hub.adapter.inbound.api.schemas.automation_schema import (
    InboundMailResult,
    InboundMailSchema,
    NewsIngestRequest,
    NewsIngestResult,
    StockScanRequest,
    StockSignalSchema,
)
from hub.app.dtos.inbound_mail_dto import InboundMailItem
from hub.app.dtos.news_dto import NewsItem
from hub.app.ports.input.mail_ingest_use_case import MailIngestUseCase
from hub.app.ports.input.news_ingest_use_case import NewsIngestUseCase
from hub.app.ports.input.signal_scan_use_case import SignalScanUseCase
from hub.adapter.inbound.api.schemas.dispatcher_schema import DispatcherResponseSchema
from hub.app.dtos.dispatcher_dto import DispatcherQuery
from hub.app.ports.input.dispatcher_use_case import DispatcherUseCase
from hub.dependencies.dispatcher_provider import get_dispatcher_use_case
from hub.dependencies.automation_provider import (
    get_mail_ingest_use_case,
    get_news_ingest_use_case,
    get_signal_scan_use_case,
)

automation_router = APIRouter(prefix="/automation", tags=["automation"])


def verify_webhook_token(
    x_webhook_token: str | None = Header(default=None, alias="X-Webhook-Token"),
) -> None:
    if N8N_INBOUND_TOKEN and x_webhook_token != N8N_INBOUND_TOKEN:
        raise HTTPException(status_code=401, detail="웹훅 토큰이 올바르지 않습니다.")


@automation_router.post(
    "/news", response_model=NewsIngestResult, summary="n8n 수집 뉴스 적재",
    dependencies=[Depends(verify_webhook_token)],
)
async def ingest_news(
    payload: NewsIngestRequest,
    use_case: NewsIngestUseCase = Depends(get_news_ingest_use_case),
) -> NewsIngestResult:
    saved = await use_case.ingest([
        NewsItem(title=i.title, source=i.source, url=i.url, published_at=i.publishedAt)
        for i in payload.items
    ])
    return NewsIngestResult(received=len(payload.items), saved=saved)


@automation_router.post(
    "/mail", response_model=InboundMailResult, summary="n8n 수신 메일 저장",
    dependencies=[Depends(verify_webhook_token)],
)
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


@automation_router.post(
    "/stock-scan", response_model=list[StockSignalSchema], summary="관심 종목 일괄 스캔",
    dependencies=[Depends(verify_webhook_token)],
)
async def scan_stocks(
    payload: StockScanRequest,
    use_case: SignalScanUseCase = Depends(get_signal_scan_use_case),
) -> list[StockSignalSchema]:
    results = await use_case.scan(payload.symbols)
    return [
        StockSignalSchema(
            symbol=r.symbol,
            price=r.price,
            direction=r.direction,
            confidence=r.confidence,
            rsi=r.rsi,
            support=r.support,
            resistance=r.resistance,
            sentimentLabel=r.sentiment_label,
        )
        for r in results
    ]


@automation_router.get("/myself", response_model=DispatcherResponseSchema)
async def introduce_myself(
    dispatcher: DispatcherUseCase = Depends(get_dispatcher_use_case)
) -> DispatcherResponseSchema:
    result = await dispatcher.introduce_myself(
        DispatcherQuery(
            id=6,
            name="자동화 창구 (hub/automation)"
        )
    )
    return DispatcherResponseSchema(
        id=result.id, name=result.name, introduction=result.introduction
    )
