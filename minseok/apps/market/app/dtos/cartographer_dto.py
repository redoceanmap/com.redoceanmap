from dataclasses import dataclass


@dataclass(frozen=True)
class CartographerQuery:

    id: int
    name: str


@dataclass(frozen=True)
class CartographerResponse:

    id: int
    name: str
    introduction: str
