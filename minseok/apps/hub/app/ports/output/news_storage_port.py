from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.news_dto import NewsItem


class NewsStoragePort(ABC):
    """허브가 스포크에 위임하는 뉴스 저장 추상.

    허브는 이 포트(추상)만 알고 어떤 스포크가 구현하는지 모른다(스타 토폴로지 허브 격리).
    구현은 스포크(stock)가 제공하고, 합성 루트(main.py)에서 주입한다.
    """

    @abstractmethod
    async def save_many(self, items: list[NewsItem]) -> int:
        """저장하고 신규 건수를 반환한다. 중복(url)은 무시한다."""
        ...
