from __future__ import annotations

from abc import ABC, abstractmethod


class JudgeCluePort(ABC):
    """저지(추론가)가 판단에 쓸 단서를 조회하는 아웃바운드 포트.

    트리아지 구현 시 유사 수신 메일(pgvector 의미 검색 등)이 단서 소스가 된다.
    구현(페이크/임베딩 검색)은 어댑터가 제공.
    """

    @abstractmethod
    async def find_clues(self, query: str, limit: int = 5) -> list[str]: ...
