from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from stock.adapter.outbound.orm.news_article_orm import NewsArticleOrm
from stock.app.ports.output.news_repository import NewsRepositoryPort
from stock.domain.entities.news_article import NewsArticle


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
                    "published_at": a.published_at,
                }
                for a in articles
            ])
            .on_conflict_do_nothing(index_elements=["url"])
            .returning(NewsArticleOrm.id)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return len(result.scalars().all())

    async def recent_titles(self, query: str, limit: int = 5) -> list[str]:
        stmt = (
            select(NewsArticleOrm.title)
            .where(NewsArticleOrm.title.ilike(f"%{query}%"))
            .order_by(NewsArticleOrm.published_at.desc().nulls_last(), NewsArticleOrm.id.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
