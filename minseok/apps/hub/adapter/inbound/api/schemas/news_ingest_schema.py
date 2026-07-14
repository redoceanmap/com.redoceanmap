from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class NewsItemSchema(BaseModel):
    title: str
    source: str = ""
    url: str
    ticker: str = ""
    publishedAt: datetime | None = None


class NewsIngestRequest(BaseModel):
    items: list[NewsItemSchema]


class NewsIngestResult(BaseModel):
    received: int
    saved: int


class NewsEmbeddingBackfillRequest(BaseModel):
    limit: int = 200


class NewsEmbeddingBackfillResult(BaseModel):
    embedded: int
