from dataclasses import dataclass


@dataclass(frozen=True)
class PostmanQuery:

    id: int
    name: str


@dataclass(frozen=True)
class PostmanResponse:

    id: int
    name: str
    introduction: str
