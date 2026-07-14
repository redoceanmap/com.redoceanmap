"""automation_router.py — 외부 자동화(n8n)의 단일 인바운드 창구.

ragwatson star_craft 패턴: 자동화는 허브만 알고, 허브 유스케이스가 스포크 구현
(포트 주입)에 위임한다. X-Webhook-Token 헤더로 호출자를 검증한다.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException

from core.config import N8N_INBOUND_TOKEN
from hub.adapter.inbound.api.schemas.automation_schema import (
    FundamentalIngestRequest,
    FundamentalIngestResult,
    InboundMailResult,
    InboundMailSchema,
    NewsEmbeddingBackfillRequest,
    NewsEmbeddingBackfillResult,
    NewsIngestRequest,
    NewsIngestResult,
    NewsLabelIngestRequest,
    NewsLabelIngestResult,
    PriceBarIngestRequest,
    PriceBarIngestResult,
    PriceCoverageSchema,
    StockScanRequest,
    StockSignalSchema,
    UnlabeledNewsSchema,
)
from hub.app.dtos.fundamental_dto import FundamentalSnapshotItem
from hub.app.dtos.inbound_mail_dto import InboundMailItem
from hub.app.dtos.news_dto import NewsItem
from hub.app.dtos.news_label_dto import NewsLabelItem
from hub.app.dtos.price_bar_dto import PriceBarItem
from hub.app.ports.input.fundamental_ingest_use_case import FundamentalIngestUseCase
from hub.app.ports.input.mail_ingest_use_case import MailIngestUseCase
from hub.app.ports.input.news_ingest_use_case import NewsIngestUseCase
from hub.app.ports.input.news_label_ingest_use_case import NewsLabelIngestUseCase
from hub.app.ports.input.price_bar_ingest_use_case import PriceBarIngestUseCase
from hub.app.ports.input.signal_scan_use_case import SignalScanUseCase
from hub.adapter.inbound.api.schemas.dispatcher_schema import DispatcherResponseSchema
from hub.app.dtos.dispatcher_dto import DispatcherQuery
from hub.app.ports.input.dispatcher_use_case import DispatcherUseCase
from hub.dependencies.dispatcher_provider import get_dispatcher_use_case
from hub.dependencies.automation_provider import (
    get_fundamental_ingest_use_case,
    get_mail_ingest_use_case,
    get_news_ingest_use_case,
    get_news_label_ingest_use_case,
    get_price_bar_ingest_use_case,
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
        NewsItem(
            title=i.title, source=i.source, url=i.url,
            ticker=i.ticker, published_at=i.publishedAt,
        )
        for i in payload.items
    ])
    return NewsIngestResult(received=len(payload.items), saved=saved)


@automation_router.post(
    "/news-embeddings/backfill", response_model=NewsEmbeddingBackfillResult,
    summary="미임베딩 뉴스 배치 임베딩 — 소급 백필/재시도",
    dependencies=[Depends(verify_webhook_token)],
)
async def backfill_news_embeddings(
    payload: NewsEmbeddingBackfillRequest,
    use_case: NewsIngestUseCase = Depends(get_news_ingest_use_case),
) -> NewsEmbeddingBackfillResult:
    embedded = await use_case.backfill_embeddings(payload.limit)
    return NewsEmbeddingBackfillResult(embedded=embedded)


@automation_router.post(
    "/prices", response_model=PriceBarIngestResult, summary="수집기 OHLCV 봉 적재",
    dependencies=[Depends(verify_webhook_token)],
)
async def ingest_prices(
    payload: PriceBarIngestRequest,
    use_case: PriceBarIngestUseCase = Depends(get_price_bar_ingest_use_case),
) -> PriceBarIngestResult:
    saved = await use_case.ingest([
        PriceBarItem(
            ticker=i.ticker, timeframe=i.timeframe, ts=i.ts,
            open=i.open, high=i.high, low=i.low, close=i.close, volume=i.volume,
        )
        for i in payload.items
    ])
    return PriceBarIngestResult(received=len(payload.items), saved=saved)


@automation_router.get(
    "/prices/coverage", response_model=list[PriceCoverageSchema],
    summary="(ticker, timeframe)별 보유 구간 — 수집기의 백필 깊이 판단용",
    dependencies=[Depends(verify_webhook_token)],
)
async def price_coverage(
    use_case: PriceBarIngestUseCase = Depends(get_price_bar_ingest_use_case),
) -> list[PriceCoverageSchema]:
    return [
        PriceCoverageSchema(
            ticker=c.ticker, timeframe=c.timeframe,
            firstTs=c.first_ts, lastTs=c.last_ts, bars=c.bars,
        )
        for c in await use_case.coverage()
    ]


@automation_router.post(
    "/news-labels", response_model=NewsLabelIngestResult, summary="라벨링 배치 뉴스 라벨 적재",
    dependencies=[Depends(verify_webhook_token)],
)
async def ingest_news_labels(
    payload: NewsLabelIngestRequest,
    use_case: NewsLabelIngestUseCase = Depends(get_news_label_ingest_use_case),
) -> NewsLabelIngestResult:
    saved = await use_case.ingest([
        NewsLabelItem(
            news_id=i.newsId, labeler=i.labeler, sentiment=i.sentiment,
            event_type=i.eventType, confidence=i.confidence,
        )
        for i in payload.items
    ])
    return NewsLabelIngestResult(received=len(payload.items), saved=saved)


@automation_router.get(
    "/news-labels/pending", response_model=list[UnlabeledNewsSchema],
    summary="라벨러별 미라벨 뉴스 — 라벨링 배치의 작업 큐",
    dependencies=[Depends(verify_webhook_token)],
)
async def pending_news_labels(
    labeler: str,
    limit: int = 500,
    use_case: NewsLabelIngestUseCase = Depends(get_news_label_ingest_use_case),
) -> list[UnlabeledNewsSchema]:
    return [
        UnlabeledNewsSchema(newsId=u.news_id, ticker=u.ticker, title=u.title)
        for u in await use_case.unlabeled(labeler, limit)
    ]


@automation_router.post(
    "/fundamentals", response_model=FundamentalIngestResult, summary="수집기 펀더멘털 스냅샷 적재",
    dependencies=[Depends(verify_webhook_token)],
)
async def ingest_fundamentals(
    payload: FundamentalIngestRequest,
    use_case: FundamentalIngestUseCase = Depends(get_fundamental_ingest_use_case),
) -> FundamentalIngestResult:
    saved = await use_case.ingest([
        FundamentalSnapshotItem(
            ticker=i.ticker, as_of=i.asOf, source=i.source,
            per=i.per, pbr=i.pbr, roe=i.roe, debt_to_equity=i.debtToEquity,
            fcf=i.fcf, market_cap=i.marketCap, eps=i.eps, bps=i.bps,
        )
        for i in payload.items
    ])
    return FundamentalIngestResult(received=len(payload.items), saved=saved)


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
