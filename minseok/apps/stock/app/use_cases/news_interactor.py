from __future__ import annotations

import logging

from stock.app.ports.input.news_use_case import NewsIngestUseCase
from stock.app.ports.output.news_repository import NewsRepositoryPort
from stock.domain.entities.news_article import NewsArticle

logger = logging.getLogger(__name__)


class NewsInteractor(NewsIngestUseCase):
    """뉴스 적재 대장. 저장(중복 무시)만 담당하고 해석은 분석 시점에 한다."""

    def __init__(self, news: NewsRepositoryPort) -> None:
        self._news = news

    async def ingest(self, articles: list[NewsArticle]) -> int:
        saved = await self._news.save_many(articles)
        logger.info("[stock-news] 수신 %d건 중 신규 %d건 저장", len(articles), saved)
        return saved
