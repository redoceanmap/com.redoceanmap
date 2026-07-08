from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Direction(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    NEUTRAL = "NEUTRAL"


@dataclass(frozen=True, slots=True)
class Outlook:
    """지표·감성으로 예측한 방향 전망 — 순수 도메인 개념. 매매 추천이 아니다."""

    direction: Direction
    confidence: float  # 0.0 ~ 1.0
