from fastapi import APIRouter, Depends, HTTPException

from auth.adapter.inbound.api.schemas.auth_schema import TokenResponse
from auth.adapter.inbound.api.schemas.social_schema import (
    SocialConsentRequest,
    SocialLoginRequest,
    SocialLoginResponse,
)
from auth.app.ports.input.social_use_case import SocialUseCase
from auth.dependencies.social_provider import get_social_use_case

social_router = APIRouter(prefix="/auth", tags=["auth"])


@social_router.post("/social/login", response_model=SocialLoginResponse)
async def social_login(
    body: SocialLoginRequest,
    use_case: SocialUseCase = Depends(get_social_use_case),
):
    try:
        result = await use_case.login(body.provider, body.code, body.redirect_uri)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    if result.status == "consent_required":
        return SocialLoginResponse(
            status="consent_required",
            consent_token=result.consent_token,
            name=result.profile.name,
            email=result.profile.email,
        )
    return SocialLoginResponse(
        status="ok",
        access_token=result.token.access_token,
        refresh_token=result.token.refresh_token,
        name=result.token.name,
        email=result.token.email,
    )


@social_router.post("/social/consent", response_model=TokenResponse)
async def social_consent(
    body: SocialConsentRequest,
    use_case: SocialUseCase = Depends(get_social_use_case),
):
    try:
        return await use_case.complete_consent(body.consent_token, body.marketing_agreed)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
