from __future__ import annotations

from abc import ABC, abstractmethod


class UnreadableImageError(Exception):
    """이미지 bytes를 디코딩하지 못함 — 계약 수준 실패 (라우터가 400으로 번역)."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class ImageClassifierPort(ABC):
    """이미지 분류 엔진 아웃바운드 포트. 구현(torchvision ConvNeXt 등)은 어댑터가 제공."""

    @abstractmethod
    def classify(self, image: bytes, top_k: int) -> list[tuple[str, float]]:
        """이미지에서 (라벨, softmax 확률) 상위 top_k를 확률 내림차순으로 반환한다.

        디코딩 불가 이미지는 UnreadableImageError로 알린다.
        """
        ...
