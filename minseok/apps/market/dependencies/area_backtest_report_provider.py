from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_market_db
from hub.app.ports.output.area_backtest_report_port import AreaBacktestReportPort
from market.adapter.outbound.gateways.area_backtest_report_gateway import (
    AreaBacktestReportGateway,
)


def get_area_backtest_report_gateway(db: AsyncSession = Depends(get_market_db)) -> AreaBacktestReportPort:
    """허브 AreaBacktestReportPort 구현 프로바이더 — main.py가 dependency_overrides로 주입."""
    return AreaBacktestReportGateway(session=db)
