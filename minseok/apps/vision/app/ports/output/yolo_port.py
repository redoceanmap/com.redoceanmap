from __future__ import annotations

from abc import ABC, abstractmethod


class YoloPort(ABC):
    """YOLO 훈련 엔진 아웃바운드 포트. 구현(ultralytics 등)은 어댑터가 제공."""

    @abstractmethod
    def train(
        self,
        base_weights: str,
        dataset_config: str,
        epochs: int,
        batch_size: int,
        image_size: int,
        device: str,
    ) -> str:
        """사전학습 가중치를 데이터셋으로 파인튜닝하고 결과 저장 디렉토리 경로를 반환한다."""
        ...

    @abstractmethod
    def predict(self, base_weights: str, image: bytes) -> list[tuple[str, float]]:
        """이미지에서 객체를 탐지해 (클래스 이름, 신뢰도) 목록을 신뢰도 내림차순으로 반환한다."""
        ...
