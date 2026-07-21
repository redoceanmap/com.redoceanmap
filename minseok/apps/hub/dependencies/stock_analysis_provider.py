from __future__ import annotations

from hub.app.ports.output.stock_analysis_port import StockAnalysisPort


def get_stock_analysis_port() -> StockAnalysisPort:
    """합성 루트(main.py)의 dependency_overrides로 스포크(stock) 구현을 주입한다.

    허브는 구체 스포크를 모르므로 여기서는 구현이 없다. override 없이 호출되면 설정 오류다.
    """
    raise NotImplementedError(
        "get_stock_analysis_port는 main.py의 dependency_overrides로 stock 구현을 주입해야 합니다."
    )


def get_stock_analysis_port_batch() -> StockAnalysisPort:
    """자동화(시그널 스캔 등) 전용 분석 포트 — 사용자 수요 기록이 없는 구현을 주입받는다.

    크론 스캔이 워치리스트 전 종목을 돌므로, 사용자 질문 수요(stock_demand)와 섞이면
    수요 편입 판단이 오염된다 — 그래서 배치 경로는 기록 없는 구현을 따로 받는다.
    """
    raise NotImplementedError(
        "get_stock_analysis_port_batch는 main.py의 dependency_overrides로 stock 구현을 주입해야 합니다."
    )
