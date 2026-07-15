from __future__ import annotations

import logging

import httpx

from core.config import GEMINI_API_KEY, GEMINI_MODEL
from hub.app.dtos.gemini_dto import GeminiAnswerResponse
from hub.app.ports.output.gemini_answer_port import GeminiAnswerError, GeminiAnswerPort

logger = logging.getLogger(__name__)

_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiApiAdapter(GeminiAnswerPort):
    """Google Gemini REST API 어댑터 — 허브 소유 전역 인프라(외부 LLM) 접속."""

    async def generate(self, prompt: str) -> GeminiAnswerResponse:
        if not GEMINI_API_KEY:
            raise GeminiAnswerError("GEMINI_API_KEY가 설정되지 않았습니다 (루트 .env)")

        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"x-goog-api-key": GEMINI_API_KEY}
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    _API_URL.format(model=GEMINI_MODEL), json=payload, headers=headers
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise GeminiAnswerError(f"Gemini API 호출 실패: {exc}") from exc

        data = response.json()
        try:
            parts = data["candidates"][0]["content"]["parts"]
            text = "".join(part.get("text", "") for part in parts).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise GeminiAnswerError(f"Gemini 응답 형식 오류: {str(data)[:200]}") from exc
        if not text:
            raise GeminiAnswerError("Gemini가 빈 답변을 반환했습니다")

        logger.info("[gemini] %s → 답변 %d자", GEMINI_MODEL, len(text))
        return GeminiAnswerResponse(answer=text, model=GEMINI_MODEL)
