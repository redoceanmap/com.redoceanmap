"""탭 온톨로지 — 등급 게이팅 대상 상단 탭의 공유 어휘.

admin(등급 탭 구성 검증)과 auth(role_tabs 영속)가 함께 쓰는 규범이라 허브 도메인에 둔다
(email_ontology 선례). 프론트 라벨·아이콘·경로는 프론트(www TopNav) 소유 — 여기는 키만.
"새로 물어보기"(/)는 게이팅 대상이 아니라 키가 없다.
"""
from __future__ import annotations

TAB_KEYS: tuple[str, ...] = ("history", "market", "stock", "vision", "automation")


def is_valid_tab(key: str) -> bool:
    return key in TAB_KEYS
