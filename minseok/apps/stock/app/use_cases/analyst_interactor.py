from __future__ import annotations

import logging

from stock.app.dtos.analyst_dto import AnalystQuery, AnalystResponse
from stock.app.ports.input.analyst_use_case import AnalystUseCase
from stock.app.ports.output.analyst_record_port import AnalystRecordPort

logger = logging.getLogger(__name__)


class AnalystInteractor(AnalystUseCase):
    """주식 분석 (stock) 대장 — 자기소개 스켈레톤. 담당: 지표+뉴스 결합 분석 — 백테스트로 검증되는 신호만."""

    def __init__(self, record: AnalystRecordPort) -> None:
        self._record = record

    async def introduce_myself(self, query: AnalystQuery) -> AnalystResponse:
        await self._record.record(subject="introduce_myself", note=f"{query.name} 자기소개 관찰")
        return AnalystResponse(
            id=query.id,
            name=query.name,
            introduction="종목의 방향 신호를 분석합니다. POST /stock/analyze — yfinance 시세(한국 .KS/.KQ + 미국)로 RSI·이동평균·지지/저항을 계산하고, 수집 뉴스와 EXAONE 감성 분석을 결합해 UP/DOWN/NEUTRAL 신호를 신호별 기여도·해석 문장과 함께 냅니다. GET /stock/{symbol}/forecast — 저장 일봉 워크포워드 백테스트로 같은 신호의 과거 상승 비율(표본·신뢰구간 병기)과 실적 분위수 예측 밴드를 제공합니다. GET /stock/{symbol}/quote — 지연 시세 현재가 폴링용. 매매 지시는 하지 않으며 확률은 과거 통계입니다.",
        )
