from __future__ import annotations

import logging

import httpx

from chat.app.use_cases.chat_interactor import _parse_llm_json
from core.config import N8N_EMAIL_WEBHOOK_URL, N8N_OUTBOUND_TOKEN
from core.llm.llm_orchestrator import llm_orchestrator
from hub.app.ports.output.email_composer_port import EmailComposerPort

logger = logging.getLogger(__name__)

_COMPOSE_PROMPT = """다음 작성 지시에 따라 이메일을 작성하라.
반드시 아래 JSON 형식으로만 응답하라 (마크다운 코드블록 없이):
{"subject": "이메일 제목 한 줄", "body": "이메일 본문 전체"}"""


class EmailComposerN8nGateway(EmailComposerPort):
    """허브 EmailComposerPort를 chat(스포크)이 구현 — LLM 작성 + n8n 웹훅 발송.

    ragwatson sherlock 패턴: Gmail 자격증명은 n8n이 보유하고 백엔드에는 비밀이 없다.
    제목/본문은 최종 사용자에게 가는 텍스트이므로 오케스트레이터 기본 모델(7.8B)로 작성한다.
    """

    async def compose_and_send(self, to_email: str, instruction: str) -> str:
        raw = await llm_orchestrator.orchestrate(
            f"{_COMPOSE_PROMPT}\n\n작성 지시: {instruction}", format="json",
        )
        parsed = _parse_llm_json(raw)
        subject = str(parsed.get("subject", "")).strip() or "redoceanmap 안내"
        body = str(parsed.get("body", "")).strip()

        detail = await self._send({"to": to_email, "subject": subject, "body": body})
        logger.info("[chat-email] to=%s subject=%r → %s", to_email, subject[:40], detail)
        return detail

    async def _send(self, payload: dict) -> str:
        headers = {"X-Webhook-Token": N8N_OUTBOUND_TOKEN}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(N8N_EMAIL_WEBHOOK_URL, json=payload, headers=headers)
            response.raise_for_status()
            return f"n8n {response.status_code}"
