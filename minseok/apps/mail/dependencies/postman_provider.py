from __future__ import annotations

from mail.adapter.outbound.log_postman_record_adapter import LogPostmanRecordAdapter
from mail.app.ports.input.postman_use_case import PostmanUseCase
from mail.app.use_cases.postman_interactor import PostmanInteractor


def get_postman_use_case() -> PostmanUseCase:
    return PostmanInteractor(record=LogPostmanRecordAdapter())
