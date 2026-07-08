"""LLM 오케스트레이터.

등록된 LLM 모델 중 하나를 선택해 추론을 수행하는 중앙 LLM 오케스트레이터.
모델을 계층에 바인딩한다: 오케스트레이터는 고품질 7.8B를 기본으로 보유하며,
최종 사용자 답변을 만드는 지점이 이 기본 모델을 쓴다. 각 도메인(스포크)은
내부 추론에서 orchestrate(model=EXAONE_2_4B)로 경량 2.4B로 내려 쓴다.
시스템 전체에 인스턴스는 하나(llm_orchestrator)이며, LLM 추론이 필요한
모든 지점이 이 오케스트레이터로 수렴한다.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from dataclasses import dataclass

from ollama import AsyncClient


@dataclass(frozen=True)
class ModelSpec:
    """오케스트레이터에 등록되는 모델 명세."""

    name: str   # Ollama 모델 태그 (예: "exaone3.5:7.8b")
    label: str  # 사람이 읽는 이름


class LLMOrchestrator:
    """등록된 모델 중 하나를 골라 채팅 추론을 수행하는 오케스트레이터."""

    def __init__(self, host: str | None = None) -> None:
        self._client = AsyncClient(host=host) if host else AsyncClient()
        self._registry: dict[str, ModelSpec] = {}
        self._default: str | None = None

    def register(self, key: str, spec: ModelSpec, *, default: bool = False) -> None:
        """모델을 레지스트리에 등록한다. 첫 등록 모델은 자동으로 기본값이 된다."""
        self._registry[key] = spec
        if default or self._default is None:
            self._default = key

    def _resolve_model(self, model: str | None) -> str:
        if model is None:
            if self._default is None:
                raise RuntimeError("등록된 모델이 없습니다. register()로 먼저 등록하세요.")
            model = self._registry[self._default].name
        return model

    def _build_messages(
        self,
        prompt: str,
        system: str | None,
        history: list[dict[str, str]] | None,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        if history:
            messages.extend(history)  # [{"role": "user"|"assistant", "content": ...}]
        messages.append({"role": "user", "content": prompt})
        return messages

    async def orchestrate(
        self,
        prompt: str,
        *,
        model: str | None = None,
        system: str | None = None,
        history: list[dict[str, str]] | None = None,
        format: str | None = None,
    ) -> str:
        """프롬프트를 추론한다. model 미지정이면 오케스트레이터 기본 모델(7.8B)로,
        도메인 내부 추론은 model=EXAONE_2_4B를 넘겨 경량 모델로 내려 쓴다.
        system/history로 멀티턴 지원. format="json"이면 유효 JSON 출력을 강제한다."""
        kwargs: dict = {}
        if format:
            kwargs["format"] = format
        response = await self._client.chat(
            model=self._resolve_model(model),
            messages=self._build_messages(prompt, system, history),
            **kwargs,
        )
        return response["message"]["content"]

    async def embed(self, text: str, *, model: str = "bge-m3") -> list[float]:
        """텍스트 임베딩(pgvector 저장·검색용). 채팅과 동일하게 오케스트레이터로 수렴한다."""
        response = await self._client.embed(model=model, input=text)
        return list(response["embeddings"][0])

    async def orchestrate_stream(
        self,
        prompt: str,
        *,
        model: str | None = None,
        system: str | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """orchestrate와 동일하되 응답을 토큰 단위로 스트리밍한다(대화형 UX용)."""
        stream = await self._client.chat(
            model=self._resolve_model(model),
            messages=self._build_messages(prompt, system, history),
            stream=True,
        )
        async for part in stream:
            chunk = part["message"]["content"]
            if chunk:
                yield chunk


# --- LLM 오케스트레이터는 하나. 기본 모델로 7.8B를 보유한다. ---
# 최종 사용자 답변은 이 기본 모델(7.8B)로 나간다.
EXAONE_3_5_7_8B = ModelSpec(name="exaone3.5:7.8b", label="EXAONE 3.5 7.8B (기본)")

# 도메인 계층(각 스포크 내부 추론)이 orchestrate(model=...)로 넘겨 쓰는 경량 태그.
EXAONE_2_4B = "exaone3.5:2.4b"

llm_orchestrator = LLMOrchestrator()
llm_orchestrator.register("exaone-7.8b", EXAONE_3_5_7_8B, default=True)  # 기본 모델(7.8B)


if __name__ == "__main__":
    import asyncio

    answer = asyncio.run(llm_orchestrator.orchestrate("한국어로 짧게 자기소개 해줘."))
    print(answer)
