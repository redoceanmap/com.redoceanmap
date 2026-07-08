from __future__ import annotations

from abc import ABC, abstractmethod

from mail.domain.entities.inbound_mail import InboundMail


class InboundMailRepositoryPort(ABC):
    """수신 메일 저장/조회 아웃바운드 포트. 구현(PG)은 어댑터가 제공."""

    @abstractmethod
    async def save(self, mail: InboundMail, embedding: list[float] | None = None) -> bool:
        """저장한다(임베딩 벡터 포함). 신규면 True, message_id 중복이면 False."""
        ...

    @abstractmethod
    async def list_recent(self, limit: int = 50) -> list[InboundMail]:
        """최신순으로 조회한다."""
        ...

    @abstractmethod
    async def search_similar(self, embedding: list[float], limit: int = 5) -> list[InboundMail]:
        """임베딩 코사인 유사도 순으로 조회한다(임베딩 없는 행 제외)."""
        ...
