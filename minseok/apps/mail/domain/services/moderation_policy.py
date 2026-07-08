from __future__ import annotations

from dataclasses import dataclass

# Unsmile 라벨 중 '유해'로 취급하는 카테고리(정책). clean은 제외.
ABUSIVE_LABELS = (
    "여성/가족", "남성", "성소수자", "인종/국적", "연령", "지역", "종교", "기타 혐오", "악플/욕설",
)
THRESHOLD = 0.5  # 시그모이드 점수 임계값


@dataclass(frozen=True)
class ModerationVerdict:
    """정책 적용 결과 — 순수 도메인 값."""

    is_abusive: bool
    categories: tuple[str, ...]  # 임계값을 넘은 유해 카테고리(점수 내림차순)


def judge(scores: dict[str, float], threshold: float = THRESHOLD) -> ModerationVerdict:
    """라벨별 점수 → 유해 판정. 외부 의존 없는 순수 함수(정책의 단일 소스)."""
    flagged = sorted(
        ((label, score) for label, score in scores.items()
         if label in ABUSIVE_LABELS and score >= threshold),
        key=lambda x: -x[1],
    )
    return ModerationVerdict(
        is_abusive=bool(flagged),
        categories=tuple(label for label, _ in flagged),
    )
