from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from hub.app.ports.output.price_bar_storage_port import PriceBarStoragePort
from stock.adapter.outbound.gateways.price_bar_storage_gateway import PriceBarStorageGateway
from stock.adapter.outbound.pg.price_bar_pg_repository import PriceBarPgRepository
from stock.app.use_cases.price_bar_interactor import PriceBarInteractor


def get_price_bar_storage_gateway(db: AsyncSession = Depends(get_db)) -> PriceBarStoragePort:
    """허브 PriceBarStoragePort 구현 프로바이더 — main.py가 dependency_overrides로 주입."""
    return PriceBarStorageGateway(
        use_case=PriceBarInteractor(bars=PriceBarPgRepository(session=db))
    )
