from dataclasses import dataclass


@dataclass(frozen=True)
class AnalystQuery:

    id: int
    name: str


@dataclass(frozen=True)
class AnalystResponse:

    id: int
    name: str
    introduction: str
