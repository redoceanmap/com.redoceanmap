from pydantic import BaseModel


class ClassificationCandidateSchema(BaseModel):

    label: str
    confidence: float


class ImageClassificationResponseSchema(BaseModel):

    filename: str
    decision: str  # auto_accepted | needs_review | human_required
    candidates: list[ClassificationCandidateSchema]
