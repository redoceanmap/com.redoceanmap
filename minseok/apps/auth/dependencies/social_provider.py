from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.adapter.outbound.gateways.social_oauth_gateway import SocialOauthGateway
from auth.adapter.outbound.pg.refresh_token_pg_repository import RefreshTokenPgRepository
from auth.adapter.outbound.pg.user_pg_repository import UserPgRepository
from auth.app.ports.input.social_use_case import SocialUseCase
from auth.app.use_cases.social_interactor import SocialInteractor
from core.database import get_db


def get_social_use_case(db: AsyncSession = Depends(get_db)) -> SocialUseCase:
    return SocialInteractor(
        profile_port=SocialOauthGateway(),
        repository=UserPgRepository(session=db),
        refresh_repository=RefreshTokenPgRepository(session=db),
    )
