from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_market_db
from hub.app.ports.output.commercial_data_port import CommercialDataPort
from market.adapter.outbound.gateways.commercial_data_gateway import CommercialDataGateway


def get_commercial_data_gateway(db: AsyncSession = Depends(get_market_db)) -> CommercialDataPort:
    return CommercialDataGateway(session=db)
