from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.grade_dto import (
    GradeCreateCommand,
    GradeDeleteCommand,
    GradeListResponse,
    GradeResponse,
    GradeUpdateCommand,
)


class GradeUseCase(ABC):

    @abstractmethod
    async def list_grades(self) -> GradeListResponse: ...

    @abstractmethod
    async def create_grade(self, command: GradeCreateCommand) -> GradeResponse: ...

    @abstractmethod
    async def update_grade(self, command: GradeUpdateCommand) -> GradeResponse: ...

    @abstractmethod
    async def delete_grade(self, command: GradeDeleteCommand) -> None: ...
