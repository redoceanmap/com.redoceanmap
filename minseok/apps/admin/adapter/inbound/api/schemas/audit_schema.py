from datetime import datetime

from pydantic import BaseModel


class AuditEntrySchema(BaseModel):
    id: int
    actor_id: int
    action: str
    detail: str
    created_at: datetime


class AuditListResponseSchema(BaseModel):
    items: list[AuditEntrySchema]
