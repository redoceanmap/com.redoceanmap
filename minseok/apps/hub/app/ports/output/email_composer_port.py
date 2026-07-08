from __future__ import annotations

from abc import ABC, abstractmethod


class EmailComposerPort(ABC):
    """허브가 스포크에 위임하는 이메일 작성·발송 추상.

    허브는 이 포트(추상)만 알고 어떤 스포크가 구현하는지 모른다(스타 토폴로지 허브 격리).
    구현은 스포크가 제공하고, 합성 루트(main.py)에서 주입한다.
    """

    @abstractmethod
    async def compose_and_send(self, to_email: str, instruction: str) -> str:
        """온톨로지 지시(instruction)를 받아 이메일을 작성·발송하고 결과 상세를 반환한다."""
        ...
