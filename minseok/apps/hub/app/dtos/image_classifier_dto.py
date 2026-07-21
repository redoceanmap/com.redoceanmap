from dataclasses import dataclass


@dataclass(frozen=True)
class ImageClassificationCommand:

    filename: str
    content: bytes


@dataclass(frozen=True)
class ClassificationCandidate:

    label: str
    confidence: float  # softmax 확률, round(4)


@dataclass(frozen=True)
class ImageClassificationResponse:

    filename: str
    decision: str  # auto_accepted | needs_review | human_required
    candidates: tuple[ClassificationCandidate, ...]  # 확률 내림차순 상위 k
