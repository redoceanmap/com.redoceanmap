from __future__ import annotations

from pydantic import BaseModel, EmailStr


class EmailRequestSchema(BaseModel):
    to: EmailStr
    content: str


class EmailRequestResultSchema(BaseModel):
    status: str
    detail: str
