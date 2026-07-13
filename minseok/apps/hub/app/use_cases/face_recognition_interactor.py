from __future__ import annotations

import logging

from hub.app.dtos.face_recognition_dto import (
    FaceMatch,
    FaceRecognitionCommand,
    FaceRecognitionResponse,
)
from hub.app.ports.input.face_recognition_use_case import FaceRecognitionUseCase
from hub.app.ports.output.yolo_port import YoloPort

logger = logging.getLogger(__name__)


class FaceRecognitionInteractor(FaceRecognitionUseCase):
    """얼굴 인식 대장 — YOLO 엔진 포트로 탐지하고 클래스 이름(사람 이름 라벨)을 답한다."""

    def __init__(self, yolo: YoloPort, weights: str) -> None:
        self._yolo = yolo
        self._weights = weights

    def recognize(self, command: FaceRecognitionCommand) -> FaceRecognitionResponse:
        predictions = self._yolo.predict(base_weights=self._weights, image=command.content)
        logger.info("얼굴 인식: file=%s, weights=%s, 탐지=%d개", command.filename, self._weights, len(predictions))

        return FaceRecognitionResponse(
            filename=command.filename,
            matches=tuple(FaceMatch(name=name, confidence=round(conf, 4)) for name, conf in predictions),
        )
