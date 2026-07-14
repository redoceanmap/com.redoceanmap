from __future__ import annotations

from fastapi import Depends

from hub.app.ports.input.mail_ingest_use_case import MailIngestUseCase
from hub.app.ports.output.mail_storage_port import MailStoragePort
from hub.app.use_cases.mail_ingest_interactor import MailIngestInteractor


def get_mail_storage_port() -> MailStoragePort:
    """합성 루트(main.py)의 dependency_overrides로 스포크(mail) 구현을 주입한다."""
    raise NotImplementedError(
        "get_mail_storage_port는 main.py의 dependency_overrides로 mail 구현을 주입해야 합니다."
    )


def get_mail_ingest_use_case(
    storage: MailStoragePort = Depends(get_mail_storage_port),
) -> MailIngestUseCase:
    return MailIngestInteractor(storage=storage)
