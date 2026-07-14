"""news_label_ingest_router.py — 라벨링 배치(cron)의 뉴스 라벨 적재·작업 큐 창구."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from hub.adapter.inbound.api.schemas.news_label_ingest_schema import (
    NewsLabelIngestRequest,
    NewsLabelIngestResult,
    UnlabeledNewsSchema,
)
from hub.adapter.inbound.api.v1.webhook_token import verify_webhook_token
from hub.app.dtos.news_label_dto import NewsLabelItem
from hub.app.ports.input.news_label_ingest_use_case import NewsLabelIngestUseCase
from hub.dependencies.news_label_ingest_provider import get_news_label_ingest_use_case

news_label_ingest_router = APIRouter(
    prefix="/automation", tags=["automation"],
    dependencies=[Depends(verify_webhook_token)],
)


@news_label_ingest_router.post(
    "/news-labels", response_model=NewsLabelIngestResult, summary="라벨링 배치 뉴스 라벨 적재",
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


@news_label_ingest_router.get(
    "/news-labels/pending", response_model=list[UnlabeledNewsSchema],
    summary="라벨러별 미라벨 뉴스 — 라벨링 배치의 작업 큐",
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
