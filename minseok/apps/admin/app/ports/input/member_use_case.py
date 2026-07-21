from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.member_dto import (
    MemberListQuery,
    MemberListResponse,
    RoleChangeCommand,
    RoleChangeResponse,
    RoleListResponse,
)


class MemberUseCase(ABC):
    """어드민 회원 관리 유스케이스 — 목록 조회 + 역할 부여/회수."""

    @abstractmethod
    async def list_members(self, query: MemberListQuery) -> MemberListResponse:
        """회원 목록(검색·페이지네이션)과 각자의 역할을 반환한다."""
        ...

    @abstractmethod
    async def list_roles(self) -> RoleListResponse:
        """역할 목록과 permission 매핑 — 부여 셀렉트·설정 페이지 공용."""
        ...

    @abstractmethod
    async def grant_role(self, command: RoleChangeCommand) -> RoleChangeResponse:
        """역할 부여(멱등). 대상 부재 시 ValueError 전파."""
        ...

    @abstractmethod
    async def revoke_role(self, command: RoleChangeCommand) -> RoleChangeResponse:
        """역할 회수(멱등). 대상 부재 시 ValueError 전파."""
        ...
