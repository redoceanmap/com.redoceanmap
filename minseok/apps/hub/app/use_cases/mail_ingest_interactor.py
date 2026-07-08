from __future__ import annotations

import logging

from hub.app.dtos.inbound_mail_dto import InboundMailItem
from hub.app.ports.input.mail_ingest_use_case import MailIngestUseCase
from hub.app.ports.output.mail_storage_port import MailStoragePort

logger = logging.getLogger(__name__)


class MailIngestInteractor(MailIngestUseCase):
    """수신 메일 허브 대장 — 저장 포트(스포크 구현)에 위임한다."""

    def __init__(self, storage: MailStoragePort) -> None:
        self._storage = storage

    async def receive(self, item: InboundMailItem) -> bool:
        saved = await self._storage.save(item)
        logger.info("[hub-mail] %s → %s", item.message_id, "신규" if saved else "중복")
        return saved
