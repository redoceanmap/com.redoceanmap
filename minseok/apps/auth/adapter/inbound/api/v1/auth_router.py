from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.adapter.inbound.api.schemas.auth_schema import LoginRequest, RegisterRequest, TokenResponse
from auth.app.ports.input.auth_use_case import AuthUseCase
from auth.dependencies.auth_provider import get_auth_use_case
from auth.adapter.inbound.api.schemas.gatekeeper_schema import GatekeeperResponseSchema
from auth.app.dtos.gatekeeper_dto import GatekeeperQuery
from auth.app.ports.input.gatekeeper_use_case import GatekeeperUseCase
from auth.dependencies.gatekeeper_provider import get_gatekeeper_use_case

auth_router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer()


@auth_router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    use_case: AuthUseCase = Depends(get_auth_use_case),
):
    try:
        return await use_case.register(body.email, body.password, body.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    use_case: AuthUseCase = Depends(get_auth_use_case),
):
    try:
        return await use_case.login(body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@auth_router.get("/me")
async def me(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    use_case: AuthUseCase = Depends(get_auth_use_case),
):
    user = await use_case.get_me(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    return {"id": user.id, "email": user.email, "name": user.name}


@auth_router.get("/myself", response_model=GatekeeperResponseSchema)
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
