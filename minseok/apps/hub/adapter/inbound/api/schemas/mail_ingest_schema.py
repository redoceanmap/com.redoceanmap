from __future__ import annotations

from pydantic import BaseModel


class InboundMailSchema(BaseModel):
    messageId: str
    subject: str = ""
    sender: str = ""
    recipient: str = ""
    preview: str = ""


class InboundMailResult(BaseModel):
    saved: bool
    messageId: str
