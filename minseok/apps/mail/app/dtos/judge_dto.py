from dataclasses import dataclass


@dataclass(frozen=True)
class JudgeQuery:

    id: int
    name: str


@dataclass(frozen=True)
class JudgeResponse:

    id: int
    name: str
    introduction: str
