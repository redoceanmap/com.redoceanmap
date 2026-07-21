from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Insight:
    """규칙 기반 해석 문장 1건 — tone은 positive | neutral | warning."""

    key: str
    tone: str
    text: str
