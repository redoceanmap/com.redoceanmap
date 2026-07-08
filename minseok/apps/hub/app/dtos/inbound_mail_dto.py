"""수신 메일 계약 DTO. 허브 자동화(n8n)가 받아 스포크(mail)에 저장을 위임한다. 순수 객체."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InboundMailItem:
    message_id: str
    subject: str
    sender: str
    recipient: str
    preview: str
