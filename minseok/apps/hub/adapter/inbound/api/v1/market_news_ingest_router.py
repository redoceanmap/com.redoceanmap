"""market_news_ingest_router.py — 상권 뉴스 수집 배치(cron)의 적재 창구."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from hub.adapter.inbound.api.schemas.market_news_ingest_schema import (
    MarketNewsIngestRequest,
    MarketNewsIngestResult,
)
from hub.adapter.inbound.api.v1.webhook_token import verify_webhook_token
from hub.app.dtos.market_news_dto import MarketNewsItem
from hub.app.ports.input.market_news_ingest_use_case import MarketNewsIngestUseCase
from hub.dependencies.market_news_ingest_provider import get_market_news_ingest_use_case

market_news_ingest_router = APIRouter(
    prefix="/automation", tags=["automation"],
    dependencies=[Depends(verify_webhook_token)],
)


@market_news_ingest_router.post(
    "/market-news", response_model=MarketNewsIngestResult, summary="수집 상권 뉴스 적재",
)
async def ingest_market_news(
    payload: MarketNewsIngestRequest,
    use_case: MarketNewsIngestUseCase = Depends(get_market_news_ingest_use_case),
) -> MarketNewsIngestResult:
    saved = await use_case.ingest([
        MarketNewsItem(
            title=i.title, source=i.source, url=i.url,
            area_tag=i.areaTag, published_at=i.publishedAt,
        )
        for i in payload.items
    ])
    return MarketNewsIngestResult(received=len(payload.items), saved=saved)
