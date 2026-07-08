from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Message:
    """대화 한 턴 — ORM/프레임워크에 의존하지 않는 도메인 엔티티."""

    id: int
    conversation_id: int
    role: str  # "user" | "assistant"
    content: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class Conversation:
    """대화 세션."""

    id: int
    created_at: datetime
