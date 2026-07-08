from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from vision.adapter.outbound.resource_adapters.yolo.ultralytics_yolo_adapter import UltralyticsYoloAdapter
from vision.app.ports.input.face_recognition_use_case import FaceRecognitionUseCase
from vision.app.use_cases.face_recognition_interactor import FaceRecognitionInteractor

# 서버는 minseok 루트에서 뜨므로 훈련 결과는 <minseok>/runs/detect/*/weights/best.pt에 쌓인다.
_RUNS_DIR = Path(__file__).resolve().parents[3] / "runs" / "detect"


def _resolve_weights() -> str:
    candidates = sorted(_RUNS_DIR.glob("*/weights/best.pt"), key=lambda p: p.stat().st_mtime)
    return str(candidates[-1]) if candidates else "yolo11n.pt"  # 파인튜닝 전엔 COCO 사전학습 가중치


@lru_cache(maxsize=1)  # 모델을 요청마다 다시 로드하지 않도록 싱글턴 유지
def get_face_recognition_use_case() -> FaceRecognitionUseCase:
    return FaceRecognitionInteractor(yolo=UltralyticsYoloAdapter(), weights=_resolve_weights())
