from __future__ import annotations

import logging

from hub.app.ports.output.semantic_record_port import SemanticRecordPort

logger = logging.getLogger(__name__)


class LogSemanticRecordAdapter(SemanticRecordPort):
    """활동 기록을 로그로 남기는 임시 구현. 영속 기록이 필요해지면 PG 어댑터로 교체."""

    async def record(self, subject: str, note: str) -> None:
        logger.info("[semantic-record] %s | %s", subject, note)
