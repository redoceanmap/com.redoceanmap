from __future__ import annotations

import io

from PIL import Image
from ultralytics import YOLO

from vision.app.ports.output.yolo_port import YoloPort


class UltralyticsYoloAdapter(YoloPort):
    """ultralytics 라이브러리로 YOLO 훈련·추론을 실행한다. 가중치는 최초 실행 시 자동 다운로드(yolo11n.pt ~5.4MB)."""

    def __init__(self) -> None:
        self._models: dict[str, YOLO] = {}

    def _model(self, base_weights: str) -> YOLO:
        if base_weights not in self._models:
            self._models[base_weights] = YOLO(base_weights)
        return self._models[base_weights]

    def train(
        self,
        base_weights: str,
        dataset_config: str,
        epochs: int,
        batch_size: int,
        image_size: int,
        device: str,
    ) -> str:
        results = self._model(base_weights).train(
            data=dataset_config,
            epochs=epochs,
            batch=batch_size,
            imgsz=image_size,
            device=device,
        )
        return str(getattr(results, "save_dir", ""))

    def predict(self, base_weights: str, image: bytes) -> list[tuple[str, float]]:
        model = self._model(base_weights)
        boxes = model(Image.open(io.BytesIO(image)))[0].boxes
        pairs = [(model.names[int(cls)], float(conf)) for cls, conf in zip(boxes.cls, boxes.conf)]
        return sorted(pairs, key=lambda pair: pair[1], reverse=True)
