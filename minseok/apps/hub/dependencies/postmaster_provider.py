from __future__ import annotations

from hub.adapter.outbound.log_postmaster_record_adapter import LogPostmasterRecordAdapter
from hub.app.ports.input.postmaster_use_case import PostmasterUseCase
from hub.app.use_cases.postmaster_interactor import PostmasterInteractor


def get_postmaster_use_case() -> PostmasterUseCase:
    return PostmasterInteractor(record=LogPostmasterRecordAdapter())
