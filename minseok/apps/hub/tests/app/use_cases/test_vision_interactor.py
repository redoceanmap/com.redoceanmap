from hub.app.dtos.vision_dto import VisionImageCommand, VisionQuery
from hub.app.use_cases.vision_interactor import VisionInteractor


class _StubRecord:
    def __init__(self):
        self.records = []

    async def record(self, subject, note):
        self.records.append((subject, note))


class _StubStorage:
    def __init__(self):
        self.saved = []

    async def save_image(self, command):
        self.saved.append(command)
        return f"vision/stub-{command.filename}"


async def test_자기소개는_배역_정보를_반환하고_기록을_남긴다():
    record = _StubRecord()
    result = await VisionInteractor(record=record, storage=_StubStorage()).introduce_myself(
        VisionQuery(id=11, name="비전 처리 (vision)")
    )
    assert result.id == 11
    assert result.name == "비전 처리 (vision)"
    assert result.introduction
    assert record.records[0][0] == "introduce_myself"


async def test_이미지_접수는_저장_후_객체_키를_반환하고_기록을_남긴다():
    record = _StubRecord()
    storage = _StubStorage()
    result = await VisionInteractor(record=record, storage=storage).analyze_image(
        VisionImageCommand(filename="cat.png", content_type="image/png", content=b"\x89PNG")
    )
    assert result.filename == "cat.png"
    assert result.content_type == "image/png"
    assert result.size_bytes == 4
    assert result.object_key == "vision/stub-cat.png"
    assert result.message
    assert storage.saved[0].filename == "cat.png"
    assert record.records[0][0] == "analyze_image"
