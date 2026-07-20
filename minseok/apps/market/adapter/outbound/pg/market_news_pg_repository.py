from __future__ import annotations

import logging

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from market.adapter.outbound.orm.market_news_article_orm import MarketNewsArticleOrm
from market.app.dtos.market_news_search_dto import MarketNewsSearchRow
from market.app.ports.output.market_news_repository import MarketNewsRepositoryPort
from market.domain.entities.market_news_article import MarketNewsArticle

logger = logging.getLogger(__name__)


class MarketNewsPgRepository(MarketNewsRepositoryPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_many(self, articles: list[MarketNewsArticle]) -> int:
        """일괄 저장. 한 행이 거부돼도 배치 전체를 잃지 않도록 행 단위로 되짚는다."""
        if not articles:
            return 0
        try:
            return await self._insert(articles)
        except DBAPIError as e:
            if e.connection_invalidated:
                raise  # 연결 유실은 행 문제가 아니다 — 되짚어봐야 전부 실패한다
            await self._session.rollback()
            return await self._insert_row_by_row(articles)

    async def _insert(self, articles: list[MarketNewsArticle]) -> int:
        stmt = (
            pg_insert(MarketNewsArticleOrm)
            .values([
                {
                    "title": a.title,
                    "source": a.source,
                    "url": a.url,
                    "area_tag": a.area_tag,
                    "published_at": a.published_at,
                }
                for a in articles
            ])
            .on_conflict_do_nothing(index_elements=["url", "area_tag"])
            .returning(MarketNewsArticleOrm.id)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return len(result.scalars().all())

    async def _insert_row_by_row(self, articles: list[MarketNewsArticle]) -> int:
        saved = 0
        for a in articles:
            try:
                saved += await self._insert([a])
            except DBAPIError as e:
                if e.connection_invalidated:
                    raise
                await self._session.rollback()
                logger.warning(
                    "[market-news] 행 거부 — 건너뜀 (area_tag=%s, url %d자): %s",
                    a.area_tag, len(a.url), e.orig,
                )
        return saved

    async def unembedded(self, limit: int) -> list[tuple[int, str]]:
        stmt = (
            select(MarketNewsArticleOrm.id, MarketNewsArticleOrm.title)
            .where(MarketNewsArticleOrm.embedding.is_(None))
            .order_by(MarketNewsArticleOrm.id.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [(row_id, title) for row_id, title in result.all()]

    async def set_embeddings(self, items: list[tuple[int, list[float]]]) -> int:
        if not items:
            return 0
        for row_id, embedding in items:
            await self._session.execute(
                update(MarketNewsArticleOrm)
                .where(MarketNewsArticleOrm.id == row_id)
                .values(embedding=embedding)
            )
        await self._session.commit()
        return len(items)

    async def search_similar(
        self, embedding: list[float], limit: int = 4
    ) -> list[MarketNewsSearchRow]:
        stmt = (
            select(MarketNewsArticleOrm)
            .where(MarketNewsArticleOrm.embedding.is_not(None))
            .order_by(MarketNewsArticleOrm.embedding.cosine_distance(embedding))
            .limit(limit * 2)  # (url, area_tag) 유니크 구조상 다행 존재 — 여유 조회 후 제목 dedupe
        )
        result = await self._session.execute(stmt)
        rows: list[MarketNewsSearchRow] = []
        seen_titles: set[str] = set()
        for orm in result.scalars().all():
            if orm.title in seen_titles:
                continue
            seen_titles.add(orm.title)
            rows.append(MarketNewsSearchRow(
                id=orm.id, title=orm.title, area_tag=orm.area_tag,
                source=orm.source, published_at=orm.published_at,
            ))
            if len(rows) >= limit:
                break
        return rows
