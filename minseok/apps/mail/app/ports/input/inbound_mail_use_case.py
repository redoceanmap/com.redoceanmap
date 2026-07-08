from __future__ import annotations

from abc import ABC, abstractmethod

from mail.domain.entities.inbound_mail import InboundMail


class InboundMailUseCase(ABC):

    @abstractmethod
    async def receive(self, mail: InboundMail) -> bool:
        """수신 메일을 저장한다. 신규 저장이면 True, 중복이면 False."""
        ...

    @abstractmethod
    async def list_mails(self, limit: int = 50) -> list[InboundMail]:
        """저장된 수신 메일을 최신순으로 조회한다."""
        ...

    @abstractmethod
    async def search_mails(self, query: str, limit: int = 5) -> list[InboundMail]:
        """질의를 임베딩해 의미가 가까운 메일 순으로 조회한다."""
        ...
