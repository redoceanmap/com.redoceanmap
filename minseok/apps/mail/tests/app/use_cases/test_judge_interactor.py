from mail.app.dtos.judge_dto import JudgeQuery
from mail.app.use_cases.judge_interactor import JudgeInteractor


class _StubClues:
    async def find_clues(self, query: str, limit: int = 5) -> list[str]:
        return ["단서1", "단서2"]


async def test_자기소개는_단서_포트를_조회해_소개문에_반영한다():
    result = await JudgeInteractor(clues=_StubClues()).introduce_myself(
        JudgeQuery(id=9, name="메일 판단기 (mail/judge)")
    )
    assert result.id == 9
    assert "판단" in result.introduction
    assert "2건" in result.introduction  # 포트가 준 단서 수가 반영된다
