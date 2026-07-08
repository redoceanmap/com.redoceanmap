from dataclasses import dataclass


@dataclass(frozen=True)
class DispatcherQuery:

    id: int
    name: str


@dataclass(frozen=True)
class DispatcherResponse:

    id: int
    name: str
    introduction: str
