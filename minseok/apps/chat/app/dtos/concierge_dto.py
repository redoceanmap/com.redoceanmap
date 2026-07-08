from dataclasses import dataclass


@dataclass(frozen=True)
class ConciergeQuery:

    id: int
    name: str


@dataclass(frozen=True)
class ConciergeResponse:

    id: int
    name: str
    introduction: str
