from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.vision_dto import (
    VisionImageCommand,
    VisionImageResponse,
    VisionQuery,
    VisionResponse,
)


class VisionUseCase(ABC):
    """비전 처리 (vision) 유스케이스 — 이미지 비전 처리."""

    @abstractmethod
    async def introduce_myself(self, query: VisionQuery) -> VisionResponse:
        """비전 처리 (vision)의 자기소개 메소드."""
        ...

    @abstractmethod
    async def analyze_image(self, command: VisionImageCommand) -> VisionImageResponse:
        """업로드된 이미지를 접수한다."""
        ...
