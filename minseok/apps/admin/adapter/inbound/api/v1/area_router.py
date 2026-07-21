from fastapi import APIRouter, Depends

from admin.adapter.inbound.api.schemas.area_schema import (
    AreaListResponseSchema,
    AreaOverviewSchema,
)
from admin.app.ports.input.area_use_case import AreaUseCase
from admin.dependencies.area_provider import get_area_use_case
from core.security import require_permission

area_router = APIRouter(prefix="/admin", tags=["admin"])


@area_router.get(
    "/areas",
    response_model=AreaListResponseSchema,
    dependencies=[Depends(require_permission("areas:read"))],
)
async def list_areas(
    use_case: AreaUseCase = Depends(get_area_use_case),
) -> AreaListResponseSchema:
    result = await use_case.list_areas()
    return AreaListResponseSchema(
        areas=[
            AreaOverviewSchema(
                trdar_code=a.trdar_code,
                trdar_name=a.trdar_name,
                gu_name=a.gu_name,
                dong_name=a.dong_name,
                store_count=a.store_count,
                closure_rate=a.closure_rate,
                monthly_sales=a.monthly_sales,
            )
            for a in result.areas
        ]
    )
