from __future__ import annotations

import logging
from pathlib import Path

from hub.app.dtos.face_training_dto import FaceTrainingCommand, FaceTrainingResponse
from hub.app.ports.input.face_training_use_case import FaceTrainingUseCase
from hub.app.ports.output.face_dataset_port import FaceDatasetPort
from hub.app.ports.output.yolo_port import YoloPort

logger = logging.getLogger(__name__)


class YoloInteractor(FaceTrainingUseCase):
    """YOLO 파인튜닝 대장 — 데이터셋·엔진 포트만 사용한다 (app 계층은 ultralytics 비의존)."""

    def __init__(self, dataset: FaceDatasetPort, yolo: YoloPort) -> None:
        self._dataset = dataset
        self._yolo = yolo

    def train(self, command: FaceTrainingCommand) -> FaceTrainingResponse:
        dataset_config = self._dataset.get_dataset_config_path()
        logger.info(
            "YOLO 파인튜닝 시작: weights=%s, data=%s, epochs=%d",
            command.base_weights, dataset_config, command.epochs,
        )

        save_dir = self._yolo.train(
            base_weights=command.base_weights,
            dataset_config=dataset_config,
            epochs=command.epochs,
            batch_size=command.batch_size,
            image_size=command.image_size,
            device=command.device,
        )

        return FaceTrainingResponse(
            dataset_config=dataset_config,
            epochs=command.epochs,
            save_dir=save_dir,
            best_weights=str(Path(save_dir) / "weights" / "best.pt") if save_dir else "",
        )
