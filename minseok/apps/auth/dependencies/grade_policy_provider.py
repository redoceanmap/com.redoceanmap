from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.adapter.outbound.gateways.grade_policy_gateway import GradePolicyGateway
from core.database import get_db
from hub.app.ports.output.grade_policy_port import GradePolicyPort


def get_grade_policy_gateway(db: AsyncSession = Depends(get_db)) -> GradePolicyPort:
    return GradePolicyGateway(session=db)
