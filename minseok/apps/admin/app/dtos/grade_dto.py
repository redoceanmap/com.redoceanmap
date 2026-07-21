from __future__ import annotations

from dataclasses import dataclass

from hub.app.dtos.grade_dto import GradeInfo


@dataclass(frozen=True)
class GradeListResponse:
    grades: list[GradeInfo]


@dataclass(frozen=True)
class GradeCreateCommand:
    actor_id: int  # 행위자(관리자) — 감사 로그 기록용
    code: str
    name: str
    tabs: tuple[str, ...]


@dataclass(frozen=True)
class GradeUpdateCommand:
    actor_id: int
    code: str
    name: str | None  # None = 유지
    tabs: tuple[str, ...] | None  # None = 유지


@dataclass(frozen=True)
class GradeDeleteCommand:
    actor_id: int
    code: str


@dataclass(frozen=True)
class GradeResponse:
    grade: GradeInfo
