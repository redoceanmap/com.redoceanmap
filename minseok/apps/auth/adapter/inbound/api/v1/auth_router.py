from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.adapter.inbound.api.schemas.auth_schema import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from auth.app.ports.input.auth_use_case import AuthUseCase
from auth.dependencies.auth_provider import get_auth_use_case

auth_router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer()
_optional_bearer = HTTPBearer(auto_error=False)  # /tabs — 비로그인도 basic 구성으로 응답


@auth_router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    use_case: AuthUseCase = Depends(get_auth_use_case),
):
    try:
        return await use_case.register(
            body.email,
            body.password,
            body.name,
            terms_agreed=body.terms_agreed,
            marketing_agreed=body.marketing_agreed,
        )
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


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    use_case: AuthUseCase = Depends(get_auth_use_case),
):
    try:
        return await use_case.refresh(body.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@auth_router.get("/tabs")
async def tabs(
    credentials: HTTPAuthorizationCredentials | None = Depends(_optional_bearer),
    use_case: AuthUseCase = Depends(get_auth_use_case),
):
    """보이는 탭 키 목록 — 등급(역할) 합집합. 토큰 없음/무효면 기본 등급(basic) 구성."""
    token = credentials.credentials if credentials else None
    return {"tabs": await use_case.get_tabs(token)}


@auth_router.get("/me")
async def me(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    use_case: AuthUseCase = Depends(get_auth_use_case),
):
    user = await use_case.get_me(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    return {"id": user.id, "email": user.email, "name": user.name}
