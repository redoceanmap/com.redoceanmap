from __future__ import annotations

import logging
import time

from hub.app.dtos.image_classifier_dto import (
    ClassificationCandidate,
    ImageClassificationCommand,
    ImageClassificationResponse,
)
from hub.app.ports.input.image_classifier_use_case import ImageClassifierUseCase
from hub.app.ports.output.image_classifier_port import ImageClassifierPort

logger = logging.getLogger(__name__)


class ImageClassifierInteractor(ImageClassifierUseCase):
    """이미지 분류 대장 — 신뢰도 게이팅(자동 확정/재확인/사람 확인)을 결정적 코드로 판정한다."""

    def __init__(
        self,
        classifier: ImageClassifierPort,
        high_confidence: float,
        low_confidence: float,
        top_k: int,
    ) -> None:
        self._classifier = classifier
        self._high_confidence = high_confidence
        self._low_confidence = low_confidence
        self._top_k = top_k

    def classify(self, command: ImageClassificationCommand) -> ImageClassificationResponse:
        started = time.perf_counter()
        predictions = self._classifier.classify(image=command.content, top_k=self._top_k)
        latency_ms = int((time.perf_counter() - started) * 1000)

        top1 = predictions[0][1] if predictions else 0.0
        if top1 >= self._high_confidence:
            decision = "auto_accepted"
        elif top1 >= self._low_confidence:
            decision = "needs_review"
        else:
            decision = "human_required"

        logger.info(
            "이미지 분류: file=%s, latency_ms=%d, top1=%.4f, decision=%s",
            command.filename, latency_ms, top1, decision,
        )
        return ImageClassificationResponse(
            filename=command.filename,
            decision=decision,
            candidates=tuple(
                ClassificationCandidate(label=label, confidence=round(conf, 4))
                for label, conf in predictions
            ),
        )
