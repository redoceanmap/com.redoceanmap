from fastapi import APIRouter, Depends, HTTPException

from admin.adapter.inbound.api.schemas.grade_schema import (
    GradeCreateRequestSchema,
    GradeListResponseSchema,
    GradeSchema,
    GradeUpdateRequestSchema,
)
from admin.app.dtos.grade_dto import (
    GradeCreateCommand,
    GradeDeleteCommand,
    GradeUpdateCommand,
)
from admin.app.exceptions import GradeProtectedError, GradeValidationError
from admin.app.ports.input.grade_use_case import GradeUseCase
from admin.dependencies.grade_provider import get_grade_use_case
from core.security import require_permission
from hub.app.dtos.grade_dto import GradeInfo

grade_router = APIRouter(prefix="/admin", tags=["admin"])


def _to_grade_schema(g: GradeInfo) -> GradeSchema:
    return GradeSchema(code=g.code, name=g.name, tabs=list(g.tabs), member_count=g.member_count)


@grade_router.get(
    "/grades",
    response_model=GradeListResponseSchema,
    dependencies=[Depends(require_permission("members:read"))],
)
async def list_grades(
    use_case: GradeUseCase = Depends(get_grade_use_case),
) -> GradeListResponseSchema:
    result = await use_case.list_grades()
    return GradeListResponseSchema(grades=[_to_grade_schema(g) for g in result.grades])


@grade_router.post("/grades", response_model=GradeSchema, status_code=201)
async def create_grade(
    body: GradeCreateRequestSchema,
    actor_id: int = Depends(require_permission("members:write")),
    use_case: GradeUseCase = Depends(get_grade_use_case),
) -> GradeSchema:
    try:
        result = await use_case.create_grade(
            GradeCreateCommand(
                actor_id=actor_id, code=body.code, name=body.name, tabs=tuple(body.tabs)
            )
        )
    except GradeValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:  # 게이트웨이 — code 중복
        raise HTTPException(status_code=409, detail=str(e))
    return _to_grade_schema(result.grade)


@grade_router.patch("/grades/{code}", response_model=GradeSchema)
async def update_grade(
    code: str,
    body: GradeUpdateRequestSchema,
    actor_id: int = Depends(require_permission("members:write")),
    use_case: GradeUseCase = Depends(get_grade_use_case),
) -> GradeSchema:
    try:
        result = await use_case.update_grade(
            GradeUpdateCommand(
                actor_id=actor_id,
                code=code,
                name=body.name,
                tabs=tuple(body.tabs) if body.tabs is not None else None,
            )
        )
    except GradeValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except GradeProtectedError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:  # 게이트웨이 — 등급 부재
        raise HTTPException(status_code=404, detail=str(e))
    return _to_grade_schema(result.grade)


@grade_router.delete("/grades/{code}")
async def delete_grade(
    code: str,
    actor_id: int = Depends(require_permission("members:write")),
    use_case: GradeUseCase = Depends(get_grade_use_case),
) -> dict:
    try:
        await use_case.delete_grade(GradeDeleteCommand(actor_id=actor_id, code=code))
    except GradeProtectedError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"deleted": code}
