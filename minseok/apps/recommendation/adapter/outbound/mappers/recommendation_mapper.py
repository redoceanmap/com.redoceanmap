from recommendation.adapter.outbound.orm.recommendation_orm import RecommendationOrm
from recommendation.domain.entities.recommendation_entity import Recommendation


class RecommendationMapper:
    """RecommendationOrm(영속성) ↔ Recommendation(도메인) 변환."""

    @staticmethod
    def to_entity(orm: RecommendationOrm) -> Recommendation:
        return Recommendation(
            id=orm.id,
            conversation_id=orm.conversation_id,
            trdar_code=orm.trdar_code,
            trdar_name=orm.trdar_name,
            district_name=orm.district_name,
            category=orm.category,
            reason=orm.reason,
            lat=orm.lat,
            lng=orm.lng,
            created_at=orm.created_at,
        )
