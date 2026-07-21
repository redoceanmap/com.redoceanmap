from __future__ import annotations

from dataclasses import dataclass

from hub.app.dtos.member_directory_dto import MemberInfo, MemberPage, RoleInfo


@dataclass(frozen=True)
class MemberListQuery:
    search: str | None
    limit: int
    offset: int


@dataclass(frozen=True)
class MemberListResponse:
    page: MemberPage


@dataclass(frozen=True)
class RoleListResponse:
    roles: list[RoleInfo]


@dataclass(frozen=True)
class RoleChangeCommand:
    actor_id: int  # 행위자(관리자) — 감사 로그 기록용
    user_id: int
    role_code: str


@dataclass(frozen=True)
class RoleChangeResponse:
    member: MemberInfo
