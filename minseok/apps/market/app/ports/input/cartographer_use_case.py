from __future__ import annotations

from abc import ABC, abstractmethod

from market.app.dtos.cartographer_dto import CartographerQuery, CartographerResponse


class CartographerUseCase(ABC):
    """상권 데이터 조회 (market) 유스케이스 — 상권 데이터의 지도 제작자 — 전국 확장의 기반."""

    @abstractmethod
    async def introduce_myself(self, query: CartographerQuery) -> CartographerResponse:
        """상권 데이터 조회 (market)의 자기소개 메소드."""
        ...
