from hub.app.dtos.image_classifier_dto import ImageClassificationCommand
from hub.app.use_cases.image_classifier_interactor import ImageClassifierInteractor


class _StubClassifierPort:
    def __init__(self, predictions):
        self._predictions = predictions
        self.classify_kwargs = None

    def classify(self, **kwargs):
        self.classify_kwargs = kwargs
        return self._predictions


def _classify(stub, high=0.85, low=0.55, top_k=5):
    interactor = ImageClassifierInteractor(
        classifier=stub, high_confidence=high, low_confidence=low, top_k=top_k
    )
    return interactor.classify(ImageClassificationCommand(filename="cat.jpg", content=b"\x89PNG"))


def test_고신뢰는_자동_확정한다():
    result = _classify(_StubClassifierPort([("tabby", 0.93), ("tiger cat", 0.04)]))

    assert result.decision == "auto_accepted"


def test_중간_신뢰는_재확인_필요로_판정한다():
    result = _classify(_StubClassifierPort([("tabby", 0.7), ("tiger cat", 0.2)]))

    assert result.decision == "needs_review"


def test_저신뢰는_사람_확인으로_에스컬레이션한다():
    result = _classify(_StubClassifierPort([("tabby", 0.3), ("tiger cat", 0.28)]))

    assert result.decision == "human_required"


def test_경계값은_이상으로_판정한다_정확히_high면_확정_정확히_low면_재확인():
    assert _classify(_StubClassifierPort([("tabby", 0.85)])).decision == "auto_accepted"
    assert _classify(_StubClassifierPort([("tabby", 0.55)])).decision == "needs_review"


def test_포트에_top_k를_전달하고_후보를_라운딩해_그대로_싣는다():
    stub = _StubClassifierPort([("tabby", 0.912345), ("tiger cat", 0.05)])

    result = _classify(stub, top_k=3)

    assert stub.classify_kwargs == {"image": b"\x89PNG", "top_k": 3}
    assert result.filename == "cat.jpg"
    assert result.candidates[0].label == "tabby"
    assert result.candidates[0].confidence == 0.9123
    assert result.candidates[1].label == "tiger cat"
