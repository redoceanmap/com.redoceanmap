from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.area_backtest_report_dto import AreaBacktestReportInfo


class AreaBacktestReportPort(ABC):
    """허브가 스포크에 위임하는 상권 백테스트 리포트 조회 추상.

    쓰기는 오프라인 배치(scripts/backtest_area_score.py)가 DB에 직접 한다(ingest 선례) —
    이 포트는 조회 전용. 구현은 market 게이트웨이, 소비는 admin의 analytics 인터랙터.
    """

    @abstractmethod
    async def latest(self) -> AreaBacktestReportInfo | None:
        """최신 실행 리포트 1건 — 실행 이력이 없으면 None."""
        ...
