from __future__ import annotations

from sqlalchemy import and_, or_, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from stock.adapter.outbound.orm.news_article_orm import NewsArticleOrm
from stock.adapter.outbound.orm.news_label_orm import NewsLabelOrm
from stock.app.dtos.news_search_dto import NewsSearchRow
from stock.app.ports.output.news_repository import NewsRepositoryPort
from stock.domain.entities.news_article import NewsArticle

DEFAULT_LABELER = "exaone-2.4b-awq"  # 검색 히트에 동반할 라벨 버전 — 상위 모델 도입 시 교체 지점


class NewsPgRepository(NewsRepositoryPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_many(self, articles: list[NewsArticle]) -> int:
        if not articles:
            return 0
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
