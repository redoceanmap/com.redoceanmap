from __future__ import annotations

import logging

from vision.app.dtos.vision_dto import (
    VisionImageCommand,
    VisionImageResponse,
    VisionQuery,
    VisionResponse,
)
from vision.app.ports.input.vision_use_case import VisionUseCase
from vision.app.ports.output.vision_record_port import VisionRecordPort
from vision.app.ports.output.vision_storage_port import VisionStoragePort

logger = logging.getLogger(__name__)


class VisionInteractor(VisionUseCase):
    """비전 처리 (vision) 대장 — 담당: 이미지 비전 처리."""

    def __init__(self, record: VisionRecordPort, storage: VisionStoragePort) -> None:
        self._record = record
        self._storage = storage

    async def introduce_myself(self, query: VisionQuery) -> VisionResponse:
        await self._record.record(subject="introduce_myself", note=f"{query.name} 자기소개 관찰")
        return VisionResponse(
            id=query.id,
            name=query.name,
            introduction="이미지 비전 처리를 담당합니다. POST /vision/images로 이미지를 접수해 S3 버킷에 저장하며(분석 파이프라인은 준비 중), GET /vision/myself 자기소개를 제공합니다. 다른 스포크와의 협력은 허브를 경유합니다.",
        )

    async def analyze_image(self, command: VisionImageCommand) -> VisionImageResponse:
        size_bytes = len(command.content)
        object_key = await self._storage.save_image(command)
        await self._record.record(
            subject="analyze_image",
            note=f"{command.filename} ({command.content_type}, {size_bytes} bytes) → {object_key} 저장",
        )
        return VisionImageResponse(
            filename=command.filename,
            content_type=command.content_type,
            size_bytes=size_bytes,
            object_key=object_key,
            message="이미지를 S3 버킷에 저장했습니다. 비전 분석 파이프라인은 준비 중입니다.",
        )
