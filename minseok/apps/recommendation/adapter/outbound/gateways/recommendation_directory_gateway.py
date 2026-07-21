from __future__ import annotations

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from hub.app.dtos.recommendation_directory_dto import (
    CategoryCount,
    MonthCount,
    RecommendationInfo,
    RecommendationStats,
)
from hub.app.ports.output.recommendation_directory_port import RecommendationDirectoryPort
from recommendation.adapter.outbound.orm.recommendation_orm import RecommendationOrm

TOP_CATEGORY_LIMIT = 6


class RecommendationDirectoryGateway(RecommendationDirectoryPort):
    """허브의 RecommendationDirectoryPort를 recommendation(스포크)이 구현한다.

    스포크 → 허브 추상에만 의존(스타 토폴로지 허용). recommendations 테이블을 집계해
    허브 계약 DTO로 반환한다.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_recent(self, limit: int) -> list[RecommendationInfo]:
        rows = (
            await self._session.execute(
                select(RecommendationOrm)
                .order_by(RecommendationOrm.created_at.desc())
                .limit(limit)
            )
        ).scalars().all()
        return [
            RecommendationInfo(
                id=r.id,
                trdar_name=r.trdar_name,
                district_name=r.district_name,
                category=r.category,
                reason=r.reason,
                created_at=r.created_at,
            )
            for r in rows
        ]

    async def stats(self) -> RecommendationStats:
        total = (
            await self._session.execute(select(func.count(RecommendationOrm.id)))
        ).scalar() or 0
        today = (
            await self._session.execute(
                select(func.count(RecommendationOrm.id)).where(
                    RecommendationOrm.created_at >= func.date_trunc("day", func.now())
                )
            )
        ).scalar() or 0

        month_expr = func.to_char(RecommendationOrm.created_at, text("'YYYY-MM'"))
        month_rows = (
            await self._session.execute(
                select(month_expr.label("month"), func.count(RecommendationOrm.id))
                .where(RecommendationOrm.created_at >= func.now() - text("interval '12 months'"))
                .group_by(month_expr)
                .order_by(month_expr)
            )
        ).all()
        monthly = [MonthCount(month=r[0], count=r[1]) for r in month_rows]

        category_rows = (
            await self._session.execute(
                select(RecommendationOrm.category, func.count(RecommendationOrm.id).label("cnt"))
                .group_by(RecommendationOrm.category)
                .order_by(func.count(RecommendationOrm.id).desc())
                .limit(TOP_CATEGORY_LIMIT)
            )
        ).all()
        top_categories = [CategoryCount(category=r[0], count=r[1]) for r in category_rows]

        return RecommendationStats(
            total=total, today=today, monthly=monthly, top_categories=top_categories
        )
