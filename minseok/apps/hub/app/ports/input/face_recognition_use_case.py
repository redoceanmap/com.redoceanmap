from __future__ import annotations

from abc import ABC, abstractmethod

from hub.app.dtos.face_recognition_dto import FaceRecognitionCommand, FaceRecognitionResponse


class FaceRecognitionUseCase(ABC):
    """얼굴 인식(객체탐지) 인바운드 포트."""

    @abstractmethod
    def recognize(self, command: FaceRecognitionCommand) -> FaceRecognitionResponse:
        """이미지에서 얼굴을 탐지하고 학습된 클래스 이름을 답한다. (CPU-bound — 호출 측에서 to_thread 분리)"""
        ...
