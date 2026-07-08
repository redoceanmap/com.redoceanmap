from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from hub.app.ports.output.recommendation_record_port import RecommendationRecordPort
from recommendation.adapter.outbound.gateways.recommendation_record_gateway import RecommendationRecordGateway
from recommendation.adapter.outbound.pg.recommendation_pg_repository import RecommendationPgRepository
from recommendation.app.ports.input.recommendation_use_case import RecommendationUseCase
from recommendation.app.use_cases.recommendation_interactor import RecommendationInteractor


def get_recommendation_use_case(
    db: AsyncSession = Depends(get_db),
) -> RecommendationUseCase:
    return RecommendationInteractor(repository=RecommendationPgRepository(session=db))


def get_recommendation_record_gateway(
    use_case: RecommendationUseCase = Depends(get_recommendation_use_case),
) -> RecommendationRecordPort:
    """허브 RecommendationRecordPort의 recommendation 구현. main.py가 주입한다."""
    return RecommendationRecordGateway(use_case=use_case)
