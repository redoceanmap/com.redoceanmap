from __future__ import annotations

from fastapi import Depends

from hub.app.ports.output.mail_storage_port import MailStoragePort
from mail.adapter.outbound.ai.kcelectra_moderation_adapter import KcElectraModerationAdapter
from mail.adapter.outbound.gateways.mail_storage_gateway import MailStorageGateway
from mail.adapter.outbound.log_watcher_record_adapter import LogWatcherRecordAdapter
from mail.app.ports.input.inbound_mail_use_case import InboundMailUseCase
from mail.app.ports.input.watcher_use_case import WatcherUseCase
from mail.app.use_cases.watcher_interactor import WatcherInteractor
from mail.dependencies.inbound_mail_provider import get_inbound_mail_use_case


def get_watcher_use_case(
    mails: InboundMailUseCase = Depends(get_inbound_mail_use_case),
) -> WatcherUseCase:
    return WatcherInteractor(
        record=LogWatcherRecordAdapter(),
        moderation=KcElectraModerationAdapter(),
        mails=mails,
    )


def get_mail_storage_gateway(
    watcher: WatcherUseCase = Depends(get_watcher_use_case),
) -> MailStoragePort:
    """허브 MailStoragePort 구현 프로바이더 — 왓처 관문 경유. main.py가 주입."""
    return MailStorageGateway(watcher=watcher)
