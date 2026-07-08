from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from vision.adapter.inbound.api.schemas.face_recognition_schema import (
    FaceMatchSchema,
    FaceRecognitionResponseSchema,
)
from vision.adapter.inbound.api.schemas.vision_schema import (
    VisionImageResponseSchema,
    VisionResponseSchema,
)
from vision.app.dtos.face_recognition_dto import FaceRecognitionCommand
from vision.app.dtos.vision_dto import VisionImageCommand, VisionQuery
from vision.app.ports.input.face_recognition_use_case import FaceRecognitionUseCase
from vision.app.ports.input.vision_use_case import VisionUseCase
from vision.dependencies.face_recognition_provider import get_face_recognition_use_case
from vision.dependencies.vision_provider import get_vision_use_case

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


@vision_router.post("/faces", response_model=FaceRecognitionResponseSchema, summary="얼굴 인식 — 객체탐지")
async def recognize_face(
    file: UploadFile = File(...),
    recognition: FaceRecognitionUseCase = Depends(get_face_recognition_use_case),
) -> FaceRecognitionResponseSchema:
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드할 수 있습니다.")
    content = await file.read()
    result = await asyncio.to_thread(
        recognition.recognize,
        FaceRecognitionCommand(filename=file.filename or "unnamed", content=content),
    )
    return FaceRecognitionResponseSchema(
        filename=result.filename,
        matches=[FaceMatchSchema(name=m.name, confidence=m.confidence) for m in result.matches],
    )
