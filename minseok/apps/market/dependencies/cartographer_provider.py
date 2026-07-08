from __future__ import annotations

from market.adapter.outbound.log_cartographer_record_adapter import LogCartographerRecordAdapter
from market.app.ports.input.cartographer_use_case import CartographerUseCase
from market.app.use_cases.cartographer_interactor import CartographerInteractor


def get_cartographer_use_case() -> CartographerUseCase:
    return CartographerInteractor(record=LogCartographerRecordAdapter())
