from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.adapter.outbound.orm.rbac_orm import (
    RolePermissionOrm,
    RoleOrm,
    RoleTabOrm,
    UserRoleOrm,
)
from hub.app.dtos.grade_dto import GradeInfo
from hub.app.ports.output.grade_policy_port import GradePolicyPort


class GradePolicyGateway(GradePolicyPort):
    """허브의 GradePolicyPort를 auth(스포크)가 구현한다.

    등급 = roles 행의 재해석. 규칙 검증(탭 키·admin 보호)은 admin 인터랙터 몫이고
    여기는 단순 CRUD만 담당한다.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_grades(self) -> list[GradeInfo]:
        rows = (
            await self._session.execute(
                select(RoleOrm.code, RoleOrm.name, RoleTabOrm.tab_key)
                .outerjoin(RoleTabOrm, RoleTabOrm.role_id == RoleOrm.id)
                .order_by(RoleOrm.id)
            )
        ).all()
        counts = dict(
            (
                await self._session.execute(
                    select(UserRoleOrm.role_id, func.count(UserRoleOrm.id)).group_by(
                        UserRoleOrm.role_id
                    )
                )
            ).all()
        )
        role_ids = dict(
            (await self._session.execute(select(RoleOrm.code, RoleOrm.id))).all()
        )
        grouped: dict[str, tuple[str, list[str]]] = {}
        for r in rows:
            grouped.setdefault(r.code, (r.name, []))
            if r.tab_key:
                grouped[r.code][1].append(r.tab_key)
        return [
            GradeInfo(
                code=code,
                name=name,
                tabs=tuple(tabs),
                member_count=counts.get(role_ids.get(code), 0),
            )
            for code, (name, tabs) in grouped.items()
        ]

    async def create_grade(self, code: str, name: str, tabs: tuple[str, ...]) -> GradeInfo:
        exists = (
            await self._session.execute(select(RoleOrm.id).where(RoleOrm.code == code))
        ).first()
        if exists:
            raise ValueError(f"이미 존재하는 등급 코드입니다: {code}")
        role = RoleOrm(code=code, name=name)
        self._session.add(role)
        await self._session.flush()  # role.id 확보
        for key in tabs:
            self._session.add(RoleTabOrm(role_id=role.id, tab_key=key))
        await self._session.commit()
        return GradeInfo(code=code, name=name, tabs=tuple(tabs), member_count=0)

    async def update_grade(
        self, code: str, name: str | None, tabs: tuple[str, ...] | None
    ) -> GradeInfo:
        role = await self._get_role(code)
        if name is not None:
            role.name = name
        if tabs is not None:
            await self._session.execute(delete(RoleTabOrm).where(RoleTabOrm.role_id == role.id))
            for key in tabs:
                self._session.add(RoleTabOrm(role_id=role.id, tab_key=key))
        await self._session.commit()
        current_tabs = (
            await self._session.execute(
                select(RoleTabOrm.tab_key).where(RoleTabOrm.role_id == role.id)
            )
        ).scalars().all()
        member_count = (
            await self._session.execute(
                select(func.count(UserRoleOrm.id)).where(UserRoleOrm.role_id == role.id)
            )
        ).scalar() or 0
        return GradeInfo(
            code=role.code, name=role.name, tabs=tuple(current_tabs), member_count=member_count
        )

    async def delete_grade(self, code: str) -> None:
        role = await self._get_role(code)
        await self._session.execute(delete(RoleTabOrm).where(RoleTabOrm.role_id == role.id))
        await self._session.execute(
            delete(RolePermissionOrm).where(RolePermissionOrm.role_id == role.id)
        )
        await self._session.execute(delete(UserRoleOrm).where(UserRoleOrm.role_id == role.id))
        await self._session.delete(role)
        await self._session.commit()

    async def _get_role(self, code: str) -> RoleOrm:
        role = (
            await self._session.execute(select(RoleOrm).where(RoleOrm.code == code))
        ).scalar_one_or_none()
        if role is None:
            raise ValueError(f"등급이 없습니다: {code}")
        return role
