from fastapi import APIRouter, Depends

from market.adapter.inbound.api.schemas.area_schema import AreaResponse
from market.app.dtos.area_dto import AreaQuery
from market.app.ports.input.area_use_case import AreaUseCase
from market.dependencies.area_provider import get_area_use_case

area_router = APIRouter(prefix="/market", tags=["market"])


@area_router.get("/areas", response_model=list[AreaResponse])
async def get_areas(
    district: str | None = None,
    use_case: AreaUseCase = Depends(get_area_use_case),
):
    return await use_case.find_all(AreaQuery(district_name=district))


@area_router.get("/trdar/{trdar_code}/area", response_model=AreaResponse)
async def get_area(
    trdar_code: int,
    use_case: AreaUseCase = Depends(get_area_use_case),
):
    return await use_case.find_by_trdar(trdar_code)
