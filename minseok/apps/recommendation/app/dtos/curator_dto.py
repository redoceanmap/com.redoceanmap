from dataclasses import dataclass


@dataclass(frozen=True)
class CuratorQuery:

    id: int
    name: str


@dataclass(frozen=True)
class CuratorResponse:

    id: int
    name: str
    introduction: str
