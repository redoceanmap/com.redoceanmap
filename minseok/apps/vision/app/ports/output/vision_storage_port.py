from __future__ import annotations

from abc import ABC, abstractmethod

from vision.app.dtos.vision_dto import VisionImageCommand


class VisionStoragePort(ABC):
    """업로드 이미지 저장 아웃바운드 포트. 구현(S3)은 어댑터가 제공."""

    @abstractmethod
    async def save_image(self, command: VisionImageCommand) -> str:
        """이미지를 저장하고 객체 키를 반환한다."""
        ...
