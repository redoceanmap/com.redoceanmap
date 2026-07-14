from __future__ import annotations

from pydantic import BaseModel


class NewsLabelSchema(BaseModel):
    newsId: int
    labeler: str  # 라벨러 버전(예: exaone-2.4b-awq)
    sentiment: float  # -1.0 ~ +1.0
    eventType: str
    confidence: float  # 0.0 ~ 1.0


class NewsLabelIngestRequest(BaseModel):
    items: list[NewsLabelSchema]


class NewsLabelIngestResult(BaseModel):
    received: int
    saved: int


class UnlabeledNewsSchema(BaseModel):
    newsId: int
    ticker: str
    title: str
