from dataclasses import dataclass


@dataclass(frozen=True)
class GatekeeperQuery:

    id: int
    name: str


@dataclass(frozen=True)
class GatekeeperResponse:

    id: int
    name: str
    introduction: str
