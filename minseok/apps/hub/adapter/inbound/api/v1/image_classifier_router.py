from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from hub.adapter.inbound.api.schemas.image_classifier_schema import (
    ClassificationCandidateSchema,
    ImageClassificationResponseSchema,
)
from hub.app.dtos.image_classifier_dto import ImageClassificationCommand
from hub.app.ports.input.image_classifier_use_case import ImageClassifierUseCase
from hub.app.ports.output.image_classifier_port import UnreadableImageError
from hub.dependencies.image_classifier_provider import get_image_classifier_use_case

image_classifier_router = APIRouter(prefix="/vision", tags=["vision"])


@image_classifier_router.post(
    "/classifications", response_model=ImageClassificationResponseSchema, summary="이미지 분류",
)
async def classify_image(
    file: UploadFile = File(...),
    classifier: ImageClassifierUseCase = Depends(get_image_classifier_use_case),
) -> ImageClassificationResponseSchema:
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드할 수 있습니다.")
    content = await file.read()
    try:
        result = await asyncio.to_thread(
            classifier.classify,
            ImageClassificationCommand(filename=file.filename or "unnamed", content=content),
        )
    except UnreadableImageError:
        raise HTTPException(status_code=400, detail="이미지를 해석할 수 없습니다.")
    return ImageClassificationResponseSchema(
        filename=result.filename,
        decision=result.decision,
        candidates=[
            ClassificationCandidateSchema(label=c.label, confidence=c.confidence)
            for c in result.candidates
        ],
    )
