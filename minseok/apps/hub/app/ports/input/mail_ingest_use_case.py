from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.inbound_mail_dto import InboundMailItem


class MailIngestUseCase(ABC):
    """자동화(n8n Gmail 파이프라인)가 보낸 수신 메일을 받아들이는 허브 유스케이스."""

    @abstractmethod
    async def receive(self, item: InboundMailItem) -> bool:
        """신규 저장이면 True, 중복이면 False."""
        ...
