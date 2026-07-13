from pathlib import Path

from hub.app.dtos.face_training_dto import FaceTrainingCommand
from hub.app.use_cases import face_training_interactor
from hub.app.use_cases.face_training_interactor import FaceTrainingInteractor


class _StubDataset:
    def __init__(self):
        self.calls = 0

    def get_dataset_config_path(self):
        self.calls += 1
        return "/data/yolo_train/data.yaml"


class _StubYolo:
    created_with = None
    train_kwargs = None

    def __init__(self, weights):
        type(self).created_with = weights

    def train(self, **kwargs):
        type(self).train_kwargs = kwargs

        class _Results:
            save_dir = "runs/detect/train"

        return _Results()


def test_훈련은_데이터셋_포트의_설정으로_YOLO_train을_실행한다(monkeypatch):
    monkeypatch.setattr(face_training_interactor, "YOLO", _StubYolo)
    dataset = _StubDataset()

    result = FaceTrainingInteractor(dataset=dataset).train(
        FaceTrainingCommand(epochs=3, batch_size=4)
    )

    assert dataset.calls == 1
    assert _StubYolo.created_with == "yolo11n.pt"
    assert _StubYolo.train_kwargs["data"] == "/data/yolo_train/data.yaml"
    assert _StubYolo.train_kwargs["epochs"] == 3
    assert _StubYolo.train_kwargs["batch"] == 4
    assert _StubYolo.train_kwargs["device"] == "cpu"
    assert result.dataset_config == "/data/yolo_train/data.yaml"
    assert result.save_dir == "runs/detect/train"
    assert result.best_weights == str(Path("runs/detect/train") / "weights" / "best.pt")
