from __future__ import annotations

from functools import lru_cache

from core.config import (
    CONVNEXT_DEVICE,
    CONVNEXT_HIGH_CONFIDENCE,
    CONVNEXT_LOW_CONFIDENCE,
    CONVNEXT_TOP_K,
)
from hub.adapter.outbound.resource_adapters.convnext.torchvision_convnext_adapter import (
    TorchvisionConvnextAdapter,
)
from hub.app.ports.input.image_classifier_use_case import ImageClassifierUseCase
from hub.app.use_cases.image_classifier_interactor import ImageClassifierInteractor


@lru_cache(maxsize=1)  # 모델을 요청마다 다시 로드하지 않도록 싱글턴 유지
def get_image_classifier_use_case() -> ImageClassifierUseCase:
    return ImageClassifierInteractor(
        classifier=TorchvisionConvnextAdapter(device=CONVNEXT_DEVICE),
        high_confidence=CONVNEXT_HIGH_CONFIDENCE,
        low_confidence=CONVNEXT_LOW_CONFIDENCE,
        top_k=CONVNEXT_TOP_K,
    )
