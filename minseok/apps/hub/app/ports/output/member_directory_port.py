from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.member_directory_dto import MemberInfo, MemberPage, MemberStats, RoleInfo


class MemberDirectoryPort(ABC):
    """허브가 스포크에 위임하는 회원·역할 조회/부여 추상.

    허브는 이 포트(추상)만 알고 어떤 스포크가 구현하는지 모른다(스타 토폴로지 허브 격리).
    구현은 users·RBAC 테이블을 소유한 스포크(auth)가 제공하고, 합성 루트(main.py)에서 주입한다.
    """

    @abstractmethod
    async def list_members(self, search: str | None, limit: int, offset: int) -> MemberPage:
        """회원 목록(이메일/이름 검색, 페이지네이션) + 각자의 role 코드를 반환한다."""
        ...

    @abstractmethod
    async def member_stats(self) -> MemberStats:
        """전체 회원 수 + 이번 달 신규 가입 수를 반환한다."""
        ...

    @abstractmethod
    async def list_roles(self) -> list[RoleInfo]:
        """역할 목록과 각 역할의 permission 코드를 반환한다."""
        ...

    @abstractmethod
    async def grant_role(self, user_id: int, role_code: str) -> MemberInfo:
        """역할을 부여하고(멱등) 갱신된 회원 정보를 반환한다. 대상 부재 시 ValueError."""
        ...

    @abstractmethod
    async def revoke_role(self, user_id: int, role_code: str) -> MemberInfo:
        """역할을 회수하고(멱등) 갱신된 회원 정보를 반환한다. 대상 부재 시 ValueError."""
        ...

    @abstractmethod
    async def list_user_permissions(self, user_id: int) -> list[str]:
        """해당 유저가 보유한 permission 코드 목록을 반환한다(비관리자는 빈 리스트)."""
        ...
