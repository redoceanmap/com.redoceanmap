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


@dataclass(frozen=True)
class SuspendCommand:
    actor_id: int
    user_id: int
    reason: str


@dataclass(frozen=True)
class MemberActionCommand:
    """대상 유저 1명에 대한 단순 행위(해제·세션 폐기·탈퇴) 공용 커맨드."""

    actor_id: int
    user_id: int


@dataclass(frozen=True)
class MemberActionResponse:
    member: MemberInfo


@dataclass(frozen=True)
class SessionRevokeResponse:
    revoked: int  # 폐기된 리프레시 토큰 수
