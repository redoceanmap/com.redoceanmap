from dataclasses import dataclass


@dataclass(frozen=True)
class FaceRecognitionCommand:

    filename: str
    content: bytes


@dataclass(frozen=True)
class FaceMatch:

    name: str  # 데이터셋 클래스 라벨 — 사람 이름으로 라벨링하면 이름을 답한다
    confidence: float


@dataclass(frozen=True)
class FaceRecognitionResponse:

    filename: str
    matches: tuple[FaceMatch, ...]
