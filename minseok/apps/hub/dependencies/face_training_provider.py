from __future__ import annotations

from pathlib import Path

from hub.adapter.outbound.resource_adapters.yolo.local_yolo_dataset_adapter import LocalYoloDatasetAdapter
from hub.adapter.outbound.resource_adapters.yolo.ultralytics_yolo_adapter import UltralyticsYoloAdapter
from hub.app.ports.input.face_training_use_case import FaceTrainingUseCase
from hub.app.use_cases.yolo_interactor import YoloInteractor

_YOLO_TRAIN_DIR = Path(__file__).resolve().parent.parent / "resources" / "yolo_train"


def get_face_training_use_case() -> FaceTrainingUseCase:
    return YoloInteractor(
        dataset=LocalYoloDatasetAdapter(base_path=_YOLO_TRAIN_DIR),
        yolo=UltralyticsYoloAdapter(),
    )
