from dataclasses import dataclass


@dataclass(frozen=True)
class GeminiQuery:

    id: int
    name: str


@dataclass(frozen=True)
class GeminiResponse:

    id: int
    name: str
    introduction: str


@dataclass(frozen=True)
class GeminiAnswerQuery:

    prompt: str


@dataclass(frozen=True)
class GeminiAnswerResponse:

    answer: str
    model: str
