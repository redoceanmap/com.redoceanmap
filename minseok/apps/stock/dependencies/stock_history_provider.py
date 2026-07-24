from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from hub.app.ports.output.fundamental_read_port import FundamentalReadPort
from stock.adapter.outbound.gateways.fundamental_read_gateway import FundamentalReadGateway
from stock.adapter.outbound.pg.stock_history_pg_repository import StockHistoryPgRepository
from stock.adapter.outbound.yfinance_market_data_adapter import YFinanceMarketDataAdapter
from stock.app.ports.input.stock_history_use_case import StockHistoryUseCase
from stock.app.use_cases.stock_history_interactor import StockHistoryInteractor


def get_stock_history_use_case(db: AsyncSession = Depends(get_db)) -> StockHistoryUseCase:
    return StockHistoryInteractor(
        history=StockHistoryPgRepository(session=db),
        market_data=YFinanceMarketDataAdapter(),  # 미수집 종목 일봉 라이브 폴백
    )


def get_fundamental_read_gateway(
    use_case: StockHistoryUseCase = Depends(get_stock_history_use_case),
) -> FundamentalReadPort:
    """허브 FundamentalReadPort 구현 프로바이더 — main.py가 dependency_overrides로 주입."""
    return FundamentalReadGateway(use_case=use_case)
