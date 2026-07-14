from fastapi import APIRouter, Depends

from stock.adapter.inbound.api.schemas.analyst_schema import AnalystResponseSchema
from stock.app.dtos.analyst_dto import AnalystQuery
from stock.app.ports.input.analyst_use_case import AnalystUseCase
from stock.dependencies.analyst_provider import get_analyst_use_case

analyst_router = APIRouter(prefix="/stock", tags=["stock"])


@analyst_router.get("/myself", response_model=AnalystResponseSchema)
async def introduce_myself(
    analyst: AnalystUseCase = Depends(get_analyst_use_case)
) -> AnalystResponseSchema:
    result = await analyst.introduce_myself(
        AnalystQuery(
            id=4,
            name="주식 분석 (stock)"
        )
    )
    return AnalystResponseSchema(
        id=result.id, name=result.name, introduction=result.introduction
    )
