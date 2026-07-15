from __future__ import annotations

import logging

from market.app.dtos.market_news_search_dto import MarketNewsSearchRow
from market.app.ports.input.market_news_use_case import MarketNewsUseCase
from market.app.ports.output.embedding_port import EmbeddingPort
from market.app.ports.output.market_news_repository import MarketNewsRepositoryPort
from market.domain.entities.market_news_article import MarketNewsArticle

logger = logging.getLogger(__name__)

EMBED_BATCH_LIMIT = 200  # 일 1회 수집 주기당 임베딩 상한 (stock 뉴스와 동일 기준)


class MarketNewsInteractor(MarketNewsUseCase):
    """상권 뉴스 적재·검색 대장. 저장(중복 무시) 후 미임베딩분을 배치 임베딩한다."""

    def __init__(
        self, news: MarketNewsRepositoryPort, embeddings: EmbeddingPort | None = None
    ) -> None:
        self._news = news
        self._embeddings = embeddings

    async def ingest(self, articles: list[MarketNewsArticle]) -> int:
        saved = await self._news.save_many(articles)
        # 신규분 + 과거 백로그(임베딩 실패분)를 일 수집 주기마다 자연 소화 — 별도 백필 불요
        embedded = await self._embed_pending()
        logger.info(
            "[market-news] 수신 %d건 중 신규 %d건 저장 / 임베딩 %d건",
            len(articles), saved, embedded,
        )
        return saved

    async def _embed_pending(self, limit: int = EMBED_BATCH_LIMIT) -> int:
        """미임베딩 행을 배치 임베딩. 실패 시 NULL 유지 — 다음 주기 재시도(수집 우선)."""
        if self._embeddings is None:
            return 0
        rows = await self._news.unembedded(limit)
        if not rows:
            return 0
        try:
            vectors = await self._embeddings.embed_many([title for _, title in rows])
        except Exception:
            logger.warning("[market-news] 임베딩 실패 — NULL 유지, 다음 주기 재시도", exc_info=True)
            return 0
        return await self._news.set_embeddings(
            [(row_id, vector) for (row_id, _), vector in zip(rows, vectors)]
        )

    async def search(self, query: str, limit: int = 4) -> list[MarketNewsSearchRow]:
        """자연어 질의 의미 검색. 임베딩 불가 시 빈 결과(검색 열화 — 예외 전파 금지)."""
        if self._embeddings is None:
            return []
        try:
            embedding = await self._embeddings.embed(query)
        except Exception:
            logger.warning("[market-news] 질의 임베딩 실패 — 빈 결과 반환", exc_info=True)
            return []
        return await self._news.search_similar(embedding, limit=limit)
