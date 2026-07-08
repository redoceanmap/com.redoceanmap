from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.adapter.outbound.pg.user_pg_repository import UserPgRepository
from auth.app.ports.input.auth_use_case import AuthUseCase
from auth.app.use_cases.auth_interactor import AuthInteractor
from core.database import get_db


def get_auth_use_case(db: AsyncSession = Depends(get_db)) -> AuthUseCase:
    return AuthInteractor(repository=UserPgRepository(session=db))
