from __future__ import annotations

from core.config import AWS_REGION, VISION_S3_BUCKET
from vision.adapter.outbound.log_vision_record_adapter import LogVisionRecordAdapter
from vision.adapter.outbound.s3_vision_storage_adapter import S3VisionStorageAdapter
from vision.app.ports.input.vision_use_case import VisionUseCase
from vision.app.use_cases.vision_interactor import VisionInteractor


def get_vision_use_case() -> VisionUseCase:
    return VisionInteractor(
        record=LogVisionRecordAdapter(),
        storage=S3VisionStorageAdapter(bucket=VISION_S3_BUCKET, region=AWS_REGION),
    )
