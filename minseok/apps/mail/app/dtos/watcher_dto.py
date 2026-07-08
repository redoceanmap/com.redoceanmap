from dataclasses import dataclass


@dataclass(frozen=True)
class WatcherQuery:

    id: int
    name: str


@dataclass(frozen=True)
class WatcherResponse:

    id: int
    name: str
    introduction: str


@dataclass(frozen=True)
class WatcherScreenResult:

    is_abusive: bool
    categories: tuple[str, ...]      # 임계값을 넘은 유해 카테고리(점수 내림차순)
    scores: dict[str, float]         # 라벨별 원시 점수(투명성)


@dataclass(frozen=True)
class WatcherMailDecision:

    blocked: bool                    # 유해 판정으로 저장이 차단됨
    saved: bool                      # 정상 통과 후 신규 저장 여부(중복이면 False)
    categories: tuple[str, ...]      # 차단 사유 카테고리
