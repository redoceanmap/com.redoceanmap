from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from hub.app.ports.output.stock_demand_port import StockDemandPort
from stock.adapter.outbound.gateways.stock_demand_gateway import StockDemandGateway


def get_stock_demand_gateway(db: AsyncSession = Depends(get_db)) -> StockDemandPort:
    """허브 StockDemandPort 구현 프로바이더 — main.py가 dependency_overrides로 주입."""
    return StockDemandGateway(session=db)
