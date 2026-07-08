from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.email_request_dto import EmailRequestCommand, EmailRequestResult


class EmailRequestUseCase(ABC):
    """이메일 발송 요청을 받는 허브 인바운드 유스케이스."""

    @abstractmethod
    async def request(self, command: EmailRequestCommand) -> EmailRequestResult: ...
