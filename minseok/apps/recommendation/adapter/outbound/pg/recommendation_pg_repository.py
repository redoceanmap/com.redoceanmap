from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from recommendation.adapter.outbound.mappers.recommendation_mapper import RecommendationMapper
from recommendation.adapter.outbound.orm.recommendation_orm import RecommendationOrm
from recommendation.app.dtos.recommendation_dto import RecommendationDraft
from recommendation.app.ports.output.recommendation_repository import RecommendationRepository
from recommendation.domain.entities.recommendation_entity import Recommendation


class RecommendationPgRepository(RecommendationRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_many(
        self, conversation_id: int | None, drafts: list[RecommendationDraft],
    ) -> list[Recommendation]:
        rows = [
            {
                "conversation_id": conversation_id,
                "trdar_code": d.trdar_code,
                "trdar_name": d.trdar_name,
                "district_name": d.district_name,
                "category": d.category,
                "reason": d.reason,
                "lat": d.lat,
                "lng": d.lng,
            }
            for d in drafts
        ]
        result = await self._session.execute(
            insert(RecommendationOrm).returning(RecommendationOrm), rows
        )
        await self._session.commit()
        return [RecommendationMapper.to_entity(o) for o in result.scalars().all()]

    async def list_recent(self, limit: int = 50) -> list[Recommendation]:
        result = await self._session.execute(
            select(RecommendationOrm).order_by(RecommendationOrm.id.desc()).limit(limit)
        )
        return [RecommendationMapper.to_entity(o) for o in result.scalars().all()]

    async def find_by_conversation(self, conversation_id: int) -> list[Recommendation]:
        result = await self._session.execute(
            select(RecommendationOrm)
            .where(RecommendationOrm.conversation_id == conversation_id)
            .order_by(RecommendationOrm.id)
        )
        return [RecommendationMapper.to_entity(o) for o in result.scalars().all()]
