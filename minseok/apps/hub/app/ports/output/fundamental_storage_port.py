from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.fundamental_dto import FundamentalSnapshotItem


class FundamentalStoragePort(ABC):
    """허브가 스포크에 위임하는 펀더멘털 스냅샷 저장 추상.

    허브는 이 포트(추상)만 알고 어떤 스포크가 구현하는지 모른다(스타 토폴로지 허브 격리).
    구현은 스포크(stock)가 제공하고, 합성 루트(main.py)에서 주입한다.
    """

    @abstractmethod
    async def save_many(self, items: list[FundamentalSnapshotItem]) -> int:
        """저장하고 신규 건수를 반환한다. (ticker, as_of, source) 중복은 무시한다."""
        ...
