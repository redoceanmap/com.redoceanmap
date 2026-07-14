from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from hub.adapter.inbound.api.schemas.face_recognition_schema import (
    FaceMatchSchema,
    FaceRecognitionResponseSchema,
)
from hub.app.dtos.face_recognition_dto import FaceRecognitionCommand
from hub.app.ports.input.face_recognition_use_case import FaceRecognitionUseCase
from hub.dependencies.face_recognition_provider import get_face_recognition_use_case

face_recognition_router = APIRouter(prefix="/vision", tags=["vision"])


@face_recognition_router.post(
    "/faces", response_model=FaceRecognitionResponseSchema, summary="얼굴 인식 — 객체탐지",
)
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
