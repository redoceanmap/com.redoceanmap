"""등급 정책 계약 DTO.

허브가 공개하는 앱 간 협력 계약의 일부. auth(스포크)가 채워서 반환하고
admin(스포크)이 소비한다. 등급 = roles 테이블의 역할 행(재해석)이다.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GradeInfo:
    code: str
    name: str
    tabs: tuple[str, ...]  # 노출 탭 키 목록 (tab_ontology.TAB_KEYS 부분집합)
    member_count: int  # 보유 회원 수 — 삭제 확인 UX용
