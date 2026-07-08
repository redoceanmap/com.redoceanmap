from __future__ import annotations

from stock.adapter.outbound.log_analyst_record_adapter import LogAnalystRecordAdapter
from stock.app.ports.input.analyst_use_case import AnalystUseCase
from stock.app.use_cases.analyst_interactor import AnalystInteractor


def get_analyst_use_case() -> AnalystUseCase:
    return AnalystInteractor(record=LogAnalystRecordAdapter())
