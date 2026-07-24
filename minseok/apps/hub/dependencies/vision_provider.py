from __future__ import annotations

from core.config import AWS_DEFAULT_REGION, VISION_S3_BUCKET
from hub.adapter.outbound.log_vision_record_adapter import LogVisionRecordAdapter
from hub.adapter.outbound.s3_vision_storage_adapter import S3VisionStorageAdapter
from hub.app.ports.input.vision_use_case import VisionUseCase
from hub.app.use_cases.vision_interactor import VisionInteractor


def get_vision_use_case() -> VisionUseCase:
    return VisionInteractor(
        record=LogVisionRecordAdapter(),
        storage=S3VisionStorageAdapter(bucket=VISION_S3_BUCKET, region=AWS_DEFAULT_REGION),
    )
