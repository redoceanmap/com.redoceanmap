from fastapi import APIRouter, Depends

from auth.adapter.inbound.api.schemas.gatekeeper_schema import GatekeeperResponseSchema
from auth.app.dtos.gatekeeper_dto import GatekeeperQuery
from auth.app.ports.input.gatekeeper_use_case import GatekeeperUseCase
from auth.dependencies.gatekeeper_provider import get_gatekeeper_use_case

gatekeeper_router = APIRouter(prefix="/auth", tags=["auth"])


@gatekeeper_router.get("/myself", response_model=GatekeeperResponseSchema)
async def introduce_myself(
    gatekeeper: GatekeeperUseCase = Depends(get_gatekeeper_use_case)
) -> GatekeeperResponseSchema:
    result = await gatekeeper.introduce_myself(
        GatekeeperQuery(
            id=1,
            name="인증 서비스 (auth)"
        )
    )
    return GatekeeperResponseSchema(
        id=result.id, name=result.name, introduction=result.introduction
    )
