from __future__ import annotations

import logging
from pathlib import Path

from ultralytics import YOLO

from hub.app.dtos.face_training_dto import FaceTrainingCommand, FaceTrainingResponse
from hub.app.ports.input.face_training_use_case import FaceTrainingUseCase
from hub.app.ports.output.face_dataset_port import FaceDatasetPort

logger = logging.getLogger(__name__)


class FaceTrainingInteractor(FaceTrainingUseCase):
    """얼굴 탐지 파인튜닝 대장 — 데이터셋 포트에서 설정을 받아 YOLO 훈련을 실행한다."""

    def __init__(self, dataset: FaceDatasetPort) -> None:
        self._dataset = dataset

    def train(self, command: FaceTrainingCommand) -> FaceTrainingResponse:
        dataset_config = self._dataset.get_dataset_config_path()
        logger.info("얼굴 탐지 파인튜닝 시작: data=%s, epochs=%d", dataset_config, command.epochs)

        model = YOLO(command.base_weights)
        results = model.train(
            data=dataset_config,
            epochs=command.epochs,
            batch=command.batch_size,
            imgsz=command.image_size,
            device=command.device,
        )

        save_dir = str(getattr(results, "save_dir", ""))
        return FaceTrainingResponse(
            dataset_config=dataset_config,
            epochs=command.epochs,
            save_dir=save_dir,
            best_weights=str(Path(save_dir) / "weights" / "best.pt") if save_dir else "",
        )
