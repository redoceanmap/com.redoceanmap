from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.inbound_mail_dto import InboundMailItem


class MailStoragePort(ABC):
    """허브가 스포크에 위임하는 수신 메일 저장 추상.

    허브는 이 포트(추상)만 알고 어떤 스포크가 구현하는지 모른다(스타 토폴로지 허브 격리).
    구현은 스포크(mail)가 제공하고, 합성 루트(main.py)에서 주입한다.
    """

    @abstractmethod
    async def save(self, item: InboundMailItem) -> bool:
        """저장한다. 신규면 True, 중복(message_id)이면 False."""
        ...
