from __future__ import annotations

from hub.adapter.outbound.log_dispatcher_record_adapter import LogDispatcherRecordAdapter
from hub.app.ports.input.dispatcher_use_case import DispatcherUseCase
from hub.app.use_cases.dispatcher_interactor import DispatcherInteractor


def get_dispatcher_use_case() -> DispatcherUseCase:
    return DispatcherInteractor(record=LogDispatcherRecordAdapter())
