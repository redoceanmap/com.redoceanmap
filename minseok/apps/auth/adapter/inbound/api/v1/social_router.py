from fastapi import APIRouter, Depends, HTTPException

from auth.adapter.inbound.api.schemas.auth_schema import TokenResponse
from auth.adapter.inbound.api.schemas.social_schema import SocialLoginRequest
from auth.app.ports.input.social_use_case import SocialUseCase
from auth.dependencies.social_provider import get_social_use_case

social_router = APIRouter(prefix="/auth", tags=["auth"])


@social_router.post("/social/login", response_model=TokenResponse)
async def social_login(
    body: SocialLoginRequest,
    use_case: SocialUseCase = Depends(get_social_use_case),
):
    try:
        return await use_case.login(body.provider, body.code, body.redirect_uri)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
