from __future__ import annotations

from abc import ABC, abstractmethod


class FaceDatasetPort(ABC):
    """얼굴 탐지 훈련 데이터셋 아웃바운드 포트. 구현(로컬 디렉토리·S3 등)은 어댑터가 제공."""

    @abstractmethod
    def get_dataset_config_path(self) -> str:
        """YOLO 훈련에 필요한 data.yaml의 절대 경로를 반환한다."""
        ...
