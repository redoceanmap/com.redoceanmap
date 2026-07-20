from __future__ import annotations

import logging

from auth.app.dtos.gatekeeper_dto import GatekeeperQuery, GatekeeperResponse
from auth.app.ports.input.gatekeeper_use_case import GatekeeperUseCase
from auth.app.ports.output.gatekeeper_record_port import GatekeeperRecordPort

logger = logging.getLogger(__name__)


class GatekeeperInteractor(GatekeeperUseCase):
    """인증 서비스 (auth) 대장 — 자기소개 스켈레톤. 담당: 인증/인가의 관문 — 로그인·토큰 검증."""

    def __init__(self, record: GatekeeperRecordPort) -> None:
        self._record = record

    async def introduce_myself(self, query: GatekeeperQuery) -> GatekeeperResponse:
        await self._record.record(subject="introduce_myself", note=f"{query.name} 자기소개 관찰")
        return GatekeeperResponse(
            id=query.id,
            name=query.name,
            introduction="회원 인증을 담당합니다. POST /auth/register 회원가입, POST /auth/login 로그인(JWT 발급), POST /auth/social/login 소셜 로그인(구글·카카오·네이버 인가 코드 교환), GET /auth/me 내 정보 조회를 제공합니다. 비밀번호는 bcrypt로 해시하고 토큰은 JWT로 검증합니다.",
        )
