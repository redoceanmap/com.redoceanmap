"""어드민 감사 로그 — 관리자 행위(역할 부여/회수 등)의 영속 기록.

admin 앱이 자체 소유하는 첫 운영 테이블. 다른 스포크 데이터가 아니라
어드민 콘솔 자신의 행위 기록이므로 허브 경유 없이 직접 영속한다.
actor_id는 users FK를 걸지 않는다(스포크 간 DB 결합 회피 — conversations 선례).
"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class AuditLogOrm(Base):
    __tablename__ = "admin_audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int] = mapped_column(Integer, index=True)
    action: Mapped[str] = mapped_column(String(50), index=True)  # 예: role.grant / role.revoke
    detail: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
