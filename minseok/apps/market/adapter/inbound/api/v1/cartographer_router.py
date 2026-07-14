from fastapi import APIRouter, Depends

from market.adapter.inbound.api.schemas.cartographer_schema import CartographerResponseSchema
from market.app.dtos.cartographer_dto import CartographerQuery
from market.app.ports.input.cartographer_use_case import CartographerUseCase
from market.dependencies.cartographer_provider import get_cartographer_use_case

cartographer_router = APIRouter(prefix="/market", tags=["market"])


@cartographer_router.get("/myself", response_model=CartographerResponseSchema)
async def introduce_myself(
    cartographer: CartographerUseCase = Depends(get_cartographer_use_case)
) -> CartographerResponseSchema:
    result = await cartographer.introduce_myself(
        CartographerQuery(
            id=3,
            name="상권 데이터 조회 (market)"
        )
    )
    return CartographerResponseSchema(
        id=result.id, name=result.name, introduction=result.introduction
    )
