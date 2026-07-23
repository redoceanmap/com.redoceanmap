from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from stock.adapter.outbound.alias_symbol_directory import AliasSymbolDirectory
from stock.adapter.outbound.pg.stock_board_pg_repository import StockBoardPgRepository
from stock.app.ports.input.stock_board_use_case import StockBoardUseCase
from stock.app.use_cases.stock_board_interactor import StockBoardInteractor


def get_stock_board_use_case(db: AsyncSession = Depends(get_db)) -> StockBoardUseCase:
    return StockBoardInteractor(
        repository=StockBoardPgRepository(session=db),
        directory=AliasSymbolDirectory(),  # 티커 → 한글명(네트워크 조회 없음)
    )
