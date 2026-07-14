"""fundamental_ingest_router.py — 수집기(cron)의 펀더멘털 스냅샷 적재 창구."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from hub.adapter.inbound.api.schemas.fundamental_ingest_schema import (
    FundamentalIngestRequest,
    FundamentalIngestResult,
)
from hub.adapter.inbound.api.v1.webhook_token import verify_webhook_token
from hub.app.dtos.fundamental_dto import FundamentalSnapshotItem
from hub.app.ports.input.fundamental_ingest_use_case import FundamentalIngestUseCase
from hub.dependencies.fundamental_ingest_provider import get_fundamental_ingest_use_case

fundamental_ingest_router = APIRouter(
    prefix="/automation", tags=["automation"],
    dependencies=[Depends(verify_webhook_token)],
)


@fundamental_ingest_router.post(
    "/fundamentals", response_model=FundamentalIngestResult, summary="수집기 펀더멘털 스냅샷 적재",
)
async def ingest_fundamentals(
    payload: FundamentalIngestRequest,
    use_case: FundamentalIngestUseCase = Depends(get_fundamental_ingest_use_case),
) -> FundamentalIngestResult:
    saved = await use_case.ingest([
        FundamentalSnapshotItem(
            ticker=i.ticker, as_of=i.asOf, source=i.source,
            per=i.per, pbr=i.pbr, roe=i.roe, debt_to_equity=i.debtToEquity,
            fcf=i.fcf, market_cap=i.marketCap, eps=i.eps, bps=i.bps,
        )
        for i in payload.items
    ])
    return FundamentalIngestResult(received=len(payload.items), saved=saved)
