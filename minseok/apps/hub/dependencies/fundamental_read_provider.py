from __future__ import annotations

from hub.app.ports.output.fundamental_read_port import FundamentalReadPort


def get_fundamental_read_port() -> FundamentalReadPort:
    """합성 루트(main.py)의 dependency_overrides로 스포크(stock) 구현을 주입한다.

    허브는 구체 스포크를 모르므로 여기서는 구현이 없다. override 없이 호출되면 설정 오류다.
    """
    raise NotImplementedError(
        "get_fundamental_read_port는 main.py의 dependency_overrides로 stock 구현을 주입해야 합니다."
    )
