from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AuditEntry:
    id: int
    actor_id: int
    action: str  # 예: role.grant / role.revoke
    detail: str
    created_at: datetime


@dataclass(frozen=True)
class AuditListQuery:
    limit: int


@dataclass(frozen=True)
class AuditListResponse:
    items: list[AuditEntry]
