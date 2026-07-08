from dataclasses import dataclass


@dataclass(frozen=True)
class PostmasterQuery:

    id: int
    name: str


@dataclass(frozen=True)
class PostmasterResponse:

    id: int
    name: str
    introduction: str
