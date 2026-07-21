from __future__ import annotations

from fastapi import Depends

from hub.app.ports.input.stock_demand_use_case import StockDemandUseCase
from hub.app.ports.output.stock_demand_port import StockDemandPort
from hub.app.use_cases.stock_demand_interactor import StockDemandInteractor


def get_stock_demand_port() -> StockDemandPort:
    """합성 루트(main.py)의 dependency_overrides로 스포크(stock) 구현을 주입한다."""
    raise NotImplementedError(
        "get_stock_demand_port는 main.py의 dependency_overrides로 stock 구현을 주입해야 합니다."
    )


def get_stock_demand_use_case(
    demand: StockDemandPort = Depends(get_stock_demand_port),
) -> StockDemandUseCase:
    return StockDemandInteractor(demand=demand)
