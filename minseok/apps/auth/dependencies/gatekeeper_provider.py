from __future__ import annotations

from auth.adapter.outbound.log_gatekeeper_record_adapter import LogGatekeeperRecordAdapter
from auth.app.ports.input.gatekeeper_use_case import GatekeeperUseCase
from auth.app.use_cases.gatekeeper_interactor import GatekeeperInteractor


def get_gatekeeper_use_case() -> GatekeeperUseCase:
    return GatekeeperInteractor(record=LogGatekeeperRecordAdapter())
