from __future__ import annotations

from abc import ABC, abstractmethod


class ModerationPort(ABC):
    """텍스트 → 유해성 라벨별 점수(0~1) 아웃바운드 포트.

    구현(KcELECTRA 분류기 등)은 어댑터가 제공. 점수의 해석(정책)은
    domain/services/moderation_policy.judge()가 담당한다.
    """

    @abstractmethod
    async def moderate(self, text: str) -> dict[str, float]: ...
