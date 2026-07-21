from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.adapter.outbound.orm.rbac_orm import RoleOrm, RoleTabOrm, UserRoleOrm
from auth.app.ports.output.grade_repository import GradeRepository

BASIC_CODE = "basic"


class GradePgRepository(GradeRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def grant_basic(self, user_id: int) -> None:
        role_id = (
            await self._session.execute(select(RoleOrm.id).where(RoleOrm.code == BASIC_CODE))
        ).scalar_one_or_none()
        if role_id is None:
            return  # 관리자가 basic을 지운 상태를 코드가 되살리지 않는다
        exists = (
            await self._session.execute(
                select(UserRoleOrm.id).where(
                    UserRoleOrm.user_id == user_id, UserRoleOrm.role_id == role_id
                )
            )
        ).first()
        if not exists:
            self._session.add(UserRoleOrm(user_id=user_id, role_id=role_id))
            await self._session.commit()

    async def visible_tabs(self, user_id: int | None) -> list[str]:
        if user_id is None:
            query = (
                select(RoleTabOrm.tab_key)
                .join(RoleOrm, RoleOrm.id == RoleTabOrm.role_id)
                .where(RoleOrm.code == BASIC_CODE)
            )
        else:
            query = (
                select(RoleTabOrm.tab_key)
                .join(UserRoleOrm, UserRoleOrm.role_id == RoleTabOrm.role_id)
                .where(UserRoleOrm.user_id == user_id)
                .distinct()
            )
        return list((await self._session.execute(query)).scalars().all())
