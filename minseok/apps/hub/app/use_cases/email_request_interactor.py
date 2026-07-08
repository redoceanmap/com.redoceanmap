from __future__ import annotations

from hub.app.dtos.email_request_dto import EmailRequestCommand, EmailRequestResult
from hub.app.ports.input.email_request_use_case import EmailRequestUseCase
from hub.app.ports.output.email_composer_port import EmailComposerPort
from hub.domain.email.email_ontology import render_instruction


class EmailRequestInteractor(EmailRequestUseCase):
    """이메일 요청 허브 대장 — 온톨로지 지시를 합성해 작성·발송 포트(스포크)에 위임한다."""

    def __init__(self, composer: EmailComposerPort) -> None:
        self._composer = composer

    async def request(self, command: EmailRequestCommand) -> EmailRequestResult:
        instruction = render_instruction(command.content)
        detail = await self._composer.compose_and_send(command.to_email, instruction)
        return EmailRequestResult(status="sent", detail=detail)
