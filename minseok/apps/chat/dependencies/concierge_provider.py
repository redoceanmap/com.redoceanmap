from __future__ import annotations

from chat.adapter.outbound.log_concierge_record_adapter import LogConciergeRecordAdapter
from chat.app.ports.input.concierge_use_case import ConciergeUseCase
from chat.app.use_cases.concierge_interactor import ConciergeInteractor


def get_concierge_use_case() -> ConciergeUseCase:
    return ConciergeInteractor(record=LogConciergeRecordAdapter())
