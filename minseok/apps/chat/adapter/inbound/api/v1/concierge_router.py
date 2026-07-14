from fastapi import APIRouter, Depends

from chat.adapter.inbound.api.schemas.concierge_schema import ConciergeResponseSchema
from chat.app.dtos.concierge_dto import ConciergeQuery
from chat.app.ports.input.concierge_use_case import ConciergeUseCase
from chat.dependencies.concierge_provider import get_concierge_use_case

concierge_router = APIRouter(prefix="/chat", tags=["chat"])


@concierge_router.get("/myself", response_model=ConciergeResponseSchema)
async def introduce_myself(
    concierge: ConciergeUseCase = Depends(get_concierge_use_case)
) -> ConciergeResponseSchema:
    result = await concierge.introduce_myself(
        ConciergeQuery(
            id=2,
            name="대화형 분석 창구 (chat)"
        )
    )
    return ConciergeResponseSchema(
        id=result.id, name=result.name, introduction=result.introduction
    )
