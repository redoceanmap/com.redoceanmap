from dataclasses import dataclass


@dataclass(frozen=True)
class VisionQuery:

    id: int
    name: str


@dataclass(frozen=True)
class VisionResponse:

    id: int
    name: str
    introduction: str


@dataclass(frozen=True)
class VisionImageCommand:

    filename: str
    content_type: str
    content: bytes


@dataclass(frozen=True)
class VisionImageResponse:

    filename: str
    content_type: str
    size_bytes: int
    object_key: str
    message: str
