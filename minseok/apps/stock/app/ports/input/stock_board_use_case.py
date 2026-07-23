from __future__ import annotations

from abc import ABC, abstractmethod

from stock.app.dtos.stock_board_dto import BoardQuery, BoardView


class StockBoardUseCase(ABC):
    """신호 보드 — 워치리스트 종목의 최신 예측 스냅샷을 한 번에 훑는다.

    종목별 analyze/forecast를 N번 부르는 대신 축적된 스냅샷을 읽어 조립한다
    (빈 워크스페이스 진입 화면용). 종목 하나를 깊게 보는 건 기존 슬라이스 몫.
    """

    @abstractmethod
    async def board(self, query: BoardQuery) -> BoardView: ...
