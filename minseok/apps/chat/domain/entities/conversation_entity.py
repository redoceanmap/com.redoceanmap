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
    payload: dict | None = None  # 답변에 곁들인 구조화 카드(추천 상권/종목) — 없으면 None


@dataclass(frozen=True, slots=True)
class Conversation:
    """대화 세션."""

    id: int
    created_at: datetime
    user_id: int | None = None  # 익명/구버전 대화는 None


@dataclass(frozen=True, slots=True)
class ConversationSummary:
    """대화 목록 한 줄 — 제목은 첫 사용자 메시지 요약."""

    id: int
    title: str
    created_at: datetime
