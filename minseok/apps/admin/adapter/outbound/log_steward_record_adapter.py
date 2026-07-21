from __future__ import annotations

import logging

from admin.app.ports.output.steward_record_port import StewardRecordPort

logger = logging.getLogger(__name__)


class LogStewardRecordAdapter(StewardRecordPort):
    """활동 기록을 로그로 남기는 임시 구현. 영속 기록이 필요해지면 PG 어댑터로 교체."""

    async def record(self, subject: str, note: str) -> None:
        logger.info("[steward-record] %s | %s", subject, note)
