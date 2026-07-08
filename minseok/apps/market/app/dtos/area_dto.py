from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AreaQuery:
    """상권 영역 목록 조회 입력 — 애플리케이션 경계의 조회 조건."""

    district_name: str | None = None
