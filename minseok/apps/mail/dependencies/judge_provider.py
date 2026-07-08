from __future__ import annotations

from mail.adapter.outbound.fake_judge_clue_adapter import FakeJudgeClueAdapter
from mail.app.ports.input.judge_use_case import JudgeUseCase
from mail.app.use_cases.judge_interactor import JudgeInteractor


def get_judge_use_case() -> JudgeUseCase:
    return JudgeInteractor(clues=FakeJudgeClueAdapter())
