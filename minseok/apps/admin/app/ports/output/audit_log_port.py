from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.audit_dto import AuditEntry


class AuditLogPort(ABC):
    """어드민 감사 로그 아웃바운드 포트 — 관리자 행위의 영속 기록/열람.

    steward의 record 포트(로그 출력, 매 요청 노이즈성 관찰)와 달리
    변경 행위(역할 부여/회수 등)만 DB에 남긴다.
    """

    @abstractmethod
    async def write(self, actor_id: int, action: str, detail: str) -> None:
        """감사 기록 1건을 영속한다."""
        ...

    @abstractmethod
    async def list_recent(self, limit: int) -> list[AuditEntry]:
        """최근 감사 기록을 최신순으로 반환한다."""
        ...
