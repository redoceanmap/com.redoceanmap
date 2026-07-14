"""news_ingest_router.py — 외부 자동화(n8n)의 뉴스 적재·임베딩 백필 창구."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from hub.adapter.inbound.api.schemas.news_ingest_schema import (
    NewsEmbeddingBackfillRequest,
    NewsEmbeddingBackfillResult,
    NewsIngestRequest,
    NewsIngestResult,
)
from hub.adapter.inbound.api.v1.webhook_token import verify_webhook_token
from hub.app.dtos.news_dto import NewsItem
from hub.app.ports.input.news_ingest_use_case import NewsIngestUseCase
from hub.dependencies.news_ingest_provider import get_news_ingest_use_case

news_ingest_router = APIRouter(
    prefix="/automation", tags=["automation"],
    dependencies=[Depends(verify_webhook_token)],
)


@news_ingest_router.post("/news", response_model=NewsIngestResult, summary="n8n 수집 뉴스 적재")
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


@news_ingest_router.post(
    "/news-embeddings/backfill", response_model=NewsEmbeddingBackfillResult,
    summary="미임베딩 뉴스 배치 임베딩 — 소급 백필/재시도",
)
async def backfill_news_embeddings(
    payload: NewsEmbeddingBackfillRequest,
    use_case: NewsIngestUseCase = Depends(get_news_ingest_use_case),
) -> NewsEmbeddingBackfillResult:
    embedded = await use_case.backfill_embeddings(payload.limit)
    return NewsEmbeddingBackfillResult(embedded=embedded)
