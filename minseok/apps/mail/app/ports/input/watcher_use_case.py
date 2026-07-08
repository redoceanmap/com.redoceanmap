from __future__ import annotations

from abc import ABC, abstractmethod

from mail.app.dtos.watcher_dto import (
    WatcherMailDecision,
    WatcherQuery,
    WatcherResponse,
    WatcherScreenResult,
)
from mail.domain.entities.inbound_mail import InboundMail


class WatcherUseCase(ABC):
    """왓처(수신 분류 관문) 유스케이스 — 설계안: [[watcher_router]] 문서 참조."""

    @abstractmethod
    async def introduce_myself(self, query: WatcherQuery) -> WatcherResponse:
        """왓처의 자기소개 메소드."""
        ...

    @abstractmethod
    async def screen(self, text: str) -> WatcherScreenResult:
        """텍스트 유해성 스크리닝 — KcELECTRA 점수에 정책(moderation_policy)을 적용한다."""
        ...

    @abstractmethod
    async def screen_and_receive(self, mail: InboundMail) -> WatcherMailDecision:
        """수신 메일 관문 — 유해면 차단, 정상이면 기존 파이프라인(임베딩→pgvector)으로 전달."""
        ...
