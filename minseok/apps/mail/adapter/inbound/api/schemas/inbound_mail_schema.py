from __future__ import annotations

from pydantic import BaseModel


class InboundMailItemSchema(BaseModel):
    id: int
    messageId: str
    subject: str
    sender: str
    recipient: str
    preview: str
    receivedAt: str
