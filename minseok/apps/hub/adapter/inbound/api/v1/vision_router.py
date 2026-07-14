from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from hub.adapter.inbound.api.schemas.vision_schema import (
    VisionImageResponseSchema,
    VisionResponseSchema,
)
from hub.app.dtos.vision_dto import VisionImageCommand, VisionQuery
from hub.app.ports.input.vision_use_case import VisionUseCase
from hub.dependencies.vision_provider import get_vision_use_case

vision_router = APIRouter(prefix="/vision", tags=["vision"])


@vision_router.get("/myself", response_model=VisionResponseSchema)
async def introduce_myself(
    vision: VisionUseCase = Depends(get_vision_use_case)
) -> VisionResponseSchema:
    result = await vision.introduce_myself(
        VisionQuery(
            id=11,
            name="비전 처리 (vision)"
        )
    )
    return VisionResponseSchema(
        id=result.id, name=result.name, introduction=result.introduction
    )


@vision_router.post("/images", response_model=VisionImageResponseSchema, summary="이미지 업로드")
async def upload_image(
    file: UploadFile = File(...),
    vision: VisionUseCase = Depends(get_vision_use_case),
) -> VisionImageResponseSchema:
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드할 수 있습니다.")
    content = await file.read()
    result = await vision.analyze_image(
        VisionImageCommand(
            filename=file.filename or "unnamed",
            content_type=file.content_type or "application/octet-stream",
            content=content,
        )
    )
    return VisionImageResponseSchema(
        filename=result.filename,
        contentType=result.content_type,
        sizeBytes=result.size_bytes,
        objectKey=result.object_key,
        message=result.message,
    )
