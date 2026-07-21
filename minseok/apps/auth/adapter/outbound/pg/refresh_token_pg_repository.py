from datetime import datetime

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.adapter.outbound.orm.refresh_token_orm import RefreshTokenOrm
from auth.app.ports.output.refresh_token_repository import RefreshTokenRepository
from auth.domain.entities.refresh_token_entity import RefreshToken


class RefreshTokenPgRepository(RefreshTokenRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        result = await self._session.execute(
            insert(RefreshTokenOrm)
            .values(user_id=user_id, token=token, expires_at=expires_at)
            .returning(RefreshTokenOrm)
        )
        await self._session.commit()
        orm = result.scalar_one()
        return RefreshToken(user_id=orm.user_id, token=orm.token, expires_at=orm.expires_at)

    async def find_by_token(self, token: str) -> RefreshToken | None:
        result = await self._session.execute(
            select(RefreshTokenOrm).where(RefreshTokenOrm.token == token)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        return RefreshToken(user_id=orm.user_id, token=orm.token, expires_at=orm.expires_at)

    async def delete(self, token: str) -> None:
        await self._session.execute(
            delete(RefreshTokenOrm).where(RefreshTokenOrm.token == token)
        )
        await self._session.commit()

    async def delete_all_for_user(self, user_id: int) -> int:
        result = await self._session.execute(
            delete(RefreshTokenOrm).where(RefreshTokenOrm.user_id == user_id)
        )
        await self._session.commit()
        return result.rowcount or 0
