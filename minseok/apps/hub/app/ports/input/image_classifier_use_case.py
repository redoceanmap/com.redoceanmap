from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.image_classifier_dto import ImageClassificationCommand, ImageClassificationResponse


class ImageClassifierUseCase(ABC):
    """이미지 분류 인바운드 포트."""

    @abstractmethod
    def classify(self, command: ImageClassificationCommand) -> ImageClassificationResponse:
        """이미지를 분류하고 신뢰도 게이팅 판정을 동봉한다. (CPU-bound — 호출 측에서 to_thread 분리)"""
        ...
