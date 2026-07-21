from __future__ import annotations

from abc import ABC, abstractmethod


class GradeRepository(ABC):
    """등급(역할) 아웃바운드 포트 — auth 스포크 내부용(가입 자동 부여·노출 탭 조회).

    등급 CRUD는 허브 GradePolicyPort(어드민 소비) 몫이고, 여기는 유저 개인 경로만 담는다.
    """

    @abstractmethod
    async def grant_basic(self, user_id: int) -> None:
        """기본 등급(basic)을 부여한다. 멱등이며 basic 역할 부재 시 무시(no-op)."""
        ...

    @abstractmethod
    async def visible_tabs(self, user_id: int | None) -> list[str]:
        """보이는 탭 키 — 보유 역할들의 합집합. None(비로그인)은 basic 구성을 반환."""
        ...
