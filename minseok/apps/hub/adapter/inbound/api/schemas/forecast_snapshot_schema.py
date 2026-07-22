from __future__ import annotations

from pydantic import BaseModel, Field


class SnapshotCaptureRequest(BaseModel):
    tickers: list[str]
    horizons: list[int] = Field(default_factory=lambda: [5])


class SnapshotCaptureResponse(BaseModel):
    captured: int
    skipped: list[str]


class SnapshotScoreResponse(BaseModel):
    scored: int
    pending: int
