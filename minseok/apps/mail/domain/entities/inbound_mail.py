from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class InboundMail:
    """수신 메일 1건. message_id(Gmail 고유 ID)가 자연 유니크 키(중복 수신 방지)."""

    message_id: str
    subject: str
    sender: str
    recipient: str
    preview: str
    id: int | None = None
    received_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.message_id:
            raise ValueError("InboundMail은 message_id가 필수입니다.")
