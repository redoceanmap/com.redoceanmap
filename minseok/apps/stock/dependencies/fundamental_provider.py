from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from hub.app.ports.output.fundamental_storage_port import FundamentalStoragePort
from stock.adapter.outbound.gateways.fundamental_storage_gateway import FundamentalStorageGateway
from stock.adapter.outbound.pg.fundamental_pg_repository import FundamentalPgRepository
from stock.app.use_cases.fundamental_interactor import FundamentalInteractor


def get_fundamental_storage_gateway(db: AsyncSession = Depends(get_db)) -> FundamentalStoragePort:
    """허브 FundamentalStoragePort 구현 프로바이더 — main.py가 dependency_overrides로 주입."""
    return FundamentalStorageGateway(
        use_case=FundamentalInteractor(fundamentals=FundamentalPgRepository(session=db))
    )
