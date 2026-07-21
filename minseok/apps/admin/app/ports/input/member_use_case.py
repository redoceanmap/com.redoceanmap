from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.member_dto import (
    MemberActionCommand,
    MemberActionResponse,
    MemberListQuery,
    MemberListResponse,
    RoleChangeCommand,
    RoleChangeResponse,
    RoleListResponse,
    SessionRevokeResponse,
    SuspendCommand,
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

    @abstractmethod
    async def suspend(self, command: SuspendCommand) -> MemberActionResponse:
        """계정 정지 + 강제 로그아웃 + 감사 기록. 해제는 reinstate."""
        ...

    @abstractmethod
    async def reinstate(self, command: MemberActionCommand) -> MemberActionResponse:
        """정지 해제(상태만 복원, 재로그인 필요) + 감사 기록."""
        ...

    @abstractmethod
    async def revoke_sessions(self, command: MemberActionCommand) -> SessionRevokeResponse:
        """리프레시 토큰 전량 폐기(강제 로그아웃) + 감사 기록."""
        ...

    @abstractmethod
    async def withdraw(self, command: MemberActionCommand) -> MemberActionResponse:
        """탈퇴 처리(개인정보 익명화, 비가역) + 감사 기록 — 이메일 접수 탈퇴 요청 처리 도구."""
        ...
