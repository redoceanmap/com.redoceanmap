from fastapi import APIRouter, Depends

from admin.adapter.inbound.api.schemas.recommendation_log_schema import (
    RecommendationLogResponseSchema,
    RecommendationLogSchema,
)
from admin.app.dtos.recommendation_log_dto import RecommendationLogQuery
from admin.app.ports.input.recommendation_log_use_case import RecommendationLogUseCase
from admin.dependencies.recommendation_log_provider import get_recommendation_log_use_case
from core.security import require_permission

recommendation_log_router = APIRouter(prefix="/admin", tags=["admin"])


@recommendation_log_router.get(
    "/recommendations",
    response_model=RecommendationLogResponseSchema,
    dependencies=[Depends(require_permission("recommendations:read"))],
)
async def list_recommendation_logs(
    limit: int = 50,
    use_case: RecommendationLogUseCase = Depends(get_recommendation_log_use_case),
) -> RecommendationLogResponseSchema:
    result = await use_case.list_logs(RecommendationLogQuery(limit=limit))
    return RecommendationLogResponseSchema(
        total=result.total,
        today=result.today,
        items=[
            RecommendationLogSchema(
                id=r.id,
                trdar_code=r.trdar_code,
                trdar_name=r.trdar_name,
                district_name=r.district_name,
                category=r.category,
                reason=r.reason,
                created_at=r.created_at,
            )
            for r in result.items
        ],
    )
