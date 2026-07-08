from __future__ import annotations

from abc import ABC, abstractmethod

from vision.app.dtos.face_training_dto import FaceTrainingCommand, FaceTrainingResponse


class FaceTrainingUseCase(ABC):
    """얼굴 탐지 파인튜닝 인바운드 포트."""

    @abstractmethod
    def train(self, command: FaceTrainingCommand) -> FaceTrainingResponse:
        """데이터셋 포트가 공급한 설정으로 YOLO 파인튜닝을 실행한다. (장시간 CPU/GPU-bound — 호출 측에서 to_thread 분리)"""
        ...
