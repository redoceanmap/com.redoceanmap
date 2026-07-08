from __future__ import annotations

from recommendation.adapter.outbound.log_curator_record_adapter import LogCuratorRecordAdapter
from recommendation.app.ports.input.curator_use_case import CuratorUseCase
from recommendation.app.use_cases.curator_interactor import CuratorInteractor


def get_curator_use_case() -> CuratorUseCase:
    return CuratorInteractor(record=LogCuratorRecordAdapter())
