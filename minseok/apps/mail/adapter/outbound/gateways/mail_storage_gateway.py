from __future__ import annotations

from hub.app.dtos.inbound_mail_dto import InboundMailItem
from hub.app.ports.output.mail_storage_port import MailStoragePort
from mail.app.ports.input.watcher_use_case import WatcherUseCase
from mail.domain.entities.inbound_mail import InboundMail


class MailStorageGateway(MailStoragePort):
    """허브 MailStoragePort 구현 — 왓처 관문을 거쳐 정상 메일만 저장 파이프라인으로.

    허브 계약 DTO → 도메인 엔티티 변환 후 WatcherUseCase.screen_and_receive에 위임.
    유해 판정 메일은 저장되지 않는다(saved=False로 응답).
    """

    def __init__(self, watcher: WatcherUseCase) -> None:
        self._watcher = watcher

    async def save(self, item: InboundMailItem) -> bool:
        decision = await self._watcher.screen_and_receive(
            InboundMail(
                message_id=item.message_id,
                subject=item.subject,
                sender=item.sender,
                recipient=item.recipient,
                preview=item.preview,
            )
        )
        return decision.saved
