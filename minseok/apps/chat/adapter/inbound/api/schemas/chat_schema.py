from datetime import datetime

from pydantic import BaseModel


class AskRequest(BaseModel):
    prompt: str
    conversationId: int | None = None


class ConversationSummarySchema(BaseModel):
    id: int
    title: str  # 첫 사용자 메시지 앞 40자
    createdAt: datetime


class ConversationMessageSchema(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    payload: dict | None = None  # 추천 상권/종목 카드 — 텍스트만인 메시지는 null
    createdAt: datetime
