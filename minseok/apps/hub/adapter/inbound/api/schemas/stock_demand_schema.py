from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class StockDemandSchema(BaseModel):
    ticker: str
    ask_count: int
    last_asked_at: datetime
