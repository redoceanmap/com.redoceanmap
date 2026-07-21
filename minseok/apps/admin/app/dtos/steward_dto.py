from dataclasses import dataclass


@dataclass(frozen=True)
class StewardQuery:

    id: int
    name: str


@dataclass(frozen=True)
class StewardResponse:

    id: int
    name: str
    introduction: str


@dataclass(frozen=True)
class StewardAccessQuery:

    user_id: int


@dataclass(frozen=True)
class StewardAccessResponse:

    user_id: int
    permissions: tuple[str, ...]  # 빈 튜플 = 비관리자
