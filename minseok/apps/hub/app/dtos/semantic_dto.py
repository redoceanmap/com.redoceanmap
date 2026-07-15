from dataclasses import dataclass


@dataclass(frozen=True)
class SemanticQuery:

    id: int
    name: str


@dataclass(frozen=True)
class SemanticResponse:

    id: int
    name: str
    introduction: str


@dataclass(frozen=True)
class SemanticAskQuery:

    prompt: str


@dataclass(frozen=True)
class SemanticRoute:
    """의도 분류 결과 — destination ∈ {crud, rag, gemini}, entities는 핵심 단어."""

    destination: str
    entities: tuple[str, ...]


@dataclass(frozen=True)
class SemanticAskResponse:

    destination: str
    entities: tuple[str, ...]
    answer: str
