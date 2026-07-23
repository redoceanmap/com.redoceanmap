from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_errors import is_infra_failure
from stock.adapter.outbound.orm.news_article_orm import NewsArticleOrm
from stock.adapter.outbound.orm.news_label_orm import NewsLabelOrm
from stock.app.dtos.news_search_dto import NewsSearchRow
from stock.app.ports.output.news_repository import NewsRepositoryPort
from stock.domain.entities.news_article import NewsArticle

logger = logging.getLogger(__name__)

DEFAULT_LABELER = "exaone-7.8b"  # 검색 히트에 동반할 라벨 버전 — 상위 모델 도입 시 교체 지점


class NewsPgRepository(NewsRepositoryPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_many(self, articles: list[NewsArticle]) -> int:
        """일괄 저장. 한 행이 거부돼도 배치 전체를 잃지 않도록 행 단위로 되짚는다."""
        if not articles:
            return 0
        try:
            return await self._insert(articles)
        except DBAPIError as e:
            if is_infra_failure(e):
                raise  # 행 문제가 아니다 — 되짚으면 전 행이 조용히 유실된다(n8n이 재시도하게)
            await self._session.rollback()
            return await self._insert_row_by_row(articles)

    async def _insert(self, articles: list[NewsArticle]) -> int:
        stmt = (
            pg_insert(NewsArticleOrm)
            .values([
                {
                    "title": a.title,
                    "source": a.source,
                    "url": a.url,
                    "ticker": a.ticker,
                    "published_at": a.published_at,
                }
                for a in articles
            ])
            .on_conflict_do_nothing(index_elements=["url", "ticker"])
            .returning(NewsArticleOrm.id)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return len(result.scalars().all())

    async def _insert_row_by_row(self, articles: list[NewsArticle]) -> int:
        saved = 0
        for a in articles:
            try:
                saved += await self._insert([a])
            except DBAPIError as e:
                if is_infra_failure(e):
                    raise  # 인프라 장애 — 남은 행도 전부 같은 이유로 실패한다
                await self._session.rollback()
                logger.warning(
                    "[stock-news] 행 거부 — 건너뜀 (ticker=%s, url %d자): %s",
                    a.ticker, len(a.url), e.orig,
                )
        return saved

    async def recent_titles(self, query: str, ticker: str = "", limit: int = 5) -> list[str]:
        # ticker 정확 일치(거래소 접미 포함) 우선 + 제목 부분 일치 폴백(티커 미기록 구버전 행)
        conditions = [NewsArticleOrm.title.ilike(f"%{query}%")]
        if ticker:
            conditions += [
                NewsArticleOrm.ticker == ticker,
                NewsArticleOrm.ticker.like(f"{ticker}.%"),
            ]
        stmt = (
            select(NewsArticleOrm.title)
            .where(or_(*conditions))
            .order_by(NewsArticleOrm.published_at.desc().nulls_last(), NewsArticleOrm.id.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def sentiment_baseline(self, ticker: str, days: int = 30) -> tuple[float | None, int]:
        since = datetime.now(UTC) - timedelta(days=days)
        avg, count = (await self._session.execute(
            select(func.avg(NewsLabelOrm.sentiment), func.count(NewsLabelOrm.id))
            .join(NewsArticleOrm, NewsLabelOrm.news_id == NewsArticleOrm.id)
            .where(
                or_(
                    NewsArticleOrm.ticker == ticker,
                    NewsArticleOrm.ticker.like(f"{ticker}.%"),  # 접미 매칭(005930 ↔ 005930.KS)
                ),
                NewsLabelOrm.labeler == DEFAULT_LABELER,
                NewsArticleOrm.published_at >= since,
            )
        )).one()
        return (float(avg) if avg is not None else None, int(count))

    async def unembedded(self, limit: int = 200) -> list[tuple[int, str]]:
        stmt = (
            select(NewsArticleOrm.id, NewsArticleOrm.title)
            .where(NewsArticleOrm.embedding.is_(None))
            .order_by(NewsArticleOrm.id.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [(row_id, title) for row_id, title in result.all()]

    async def set_embeddings(self, items: list[tuple[int, list[float]]]) -> int:
        if not items:
            return 0
        for row_id, embedding in items:
            await self._session.execute(
                update(NewsArticleOrm)
                .where(NewsArticleOrm.id == row_id)
                .values(embedding=embedding)
            )
        await self._session.commit()
        return len(items)

    async def search_similar(
        self, embedding: list[float], ticker: str | None = None, limit: int = 5,
    ) -> list[NewsSearchRow]:
        conditions = [NewsArticleOrm.embedding.is_not(None)]
        if ticker:
            # recent_titles와 동일한 거래소 접미 규칙(005930 ↔ 005930.KS)
            conditions.append(or_(
                NewsArticleOrm.ticker == ticker,
                NewsArticleOrm.ticker.like(f"{ticker}.%"),
            ))
        stmt = (
            select(NewsArticleOrm, NewsLabelOrm.sentiment, NewsLabelOrm.event_type)
            .outerjoin(NewsLabelOrm, and_(
                NewsLabelOrm.news_id == NewsArticleOrm.id,
                NewsLabelOrm.labeler == DEFAULT_LABELER,
            ))
            .where(*conditions)
            .order_by(NewsArticleOrm.embedding.cosine_distance(embedding))
            .limit(limit * 2)  # 같은 기사가 (url, ticker) 유니크 구조상 다행 존재 — 여유 조회 후 제목 dedupe
        )
        result = await self._session.execute(stmt)
        rows: list[NewsSearchRow] = []
        seen_titles: set[str] = set()
        for orm, sentiment, event_type in result.all():
            if orm.title in seen_titles:
                continue
            seen_titles.add(orm.title)
            rows.append(NewsSearchRow(
                id=orm.id, title=orm.title, ticker=orm.ticker, source=orm.source,
                published_at=orm.published_at, sentiment=sentiment, event_type=event_type,
            ))
            if len(rows) >= limit:
                break
        return rows
