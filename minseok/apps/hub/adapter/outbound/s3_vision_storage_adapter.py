from __future__ import annotations

import asyncio
import uuid
from pathlib import PurePosixPath

import boto3

from hub.app.dtos.vision_dto import VisionImageCommand
from hub.app.ports.output.vision_storage_port import VisionStoragePort


class S3VisionStorageAdapter(VisionStoragePort):
    """업로드 이미지를 S3 버킷에 저장한다. 자격 증명은 boto3 기본 체인(env)을 쓴다."""

    def __init__(self, bucket: str, region: str) -> None:
        self._bucket = bucket
        self._client = boto3.client("s3", region_name=region)

    async def save_image(self, command: VisionImageCommand) -> str:
        ext = PurePosixPath(command.filename).suffix.lower()
        key = f"vision/{uuid.uuid4().hex}{ext}"
        # boto3는 동기 클라이언트 — 이벤트 루프를 막지 않게 스레드로 분리
        await asyncio.to_thread(
            self._client.put_object,
            Bucket=self._bucket,
            Key=key,
            Body=command.content,
            ContentType=command.content_type,
        )
        return key
