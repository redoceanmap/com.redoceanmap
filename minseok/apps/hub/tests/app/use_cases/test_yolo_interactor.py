from pathlib import Path

from hub.app.dtos.face_training_dto import FaceTrainingCommand
from hub.app.use_cases.yolo_interactor import YoloInteractor


class _StubDataset:
    def __init__(self):
        self.calls = 0

    def get_dataset_config_path(self):
        self.calls += 1
        return "/data/yolo_train/data.yaml"


class _StubYoloPort:
    def __init__(self):
        self.train_kwargs = None

    def train(self, **kwargs):
        self.train_kwargs = kwargs
        return "runs/detect/train"


def test_훈련은_포트에서_받은_설정으로_yolo11n을_파인튜닝한다():
    dataset = _StubDataset()
    yolo = _StubYoloPort()

    result = YoloInteractor(dataset=dataset, yolo=yolo).train(
        FaceTrainingCommand(epochs=3, batch_size=4)
    )

    assert dataset.calls == 1
    assert yolo.train_kwargs["base_weights"] == "yolo11n.pt"
    assert yolo.train_kwargs["dataset_config"] == "/data/yolo_train/data.yaml"
    assert yolo.train_kwargs["epochs"] == 3
    assert yolo.train_kwargs["batch_size"] == 4
    assert yolo.train_kwargs["image_size"] == 640
    assert yolo.train_kwargs["device"] == "cpu"
    assert result.dataset_config == "/data/yolo_train/data.yaml"
    assert result.save_dir == "runs/detect/train"
    assert result.best_weights == str(Path("runs/detect/train") / "weights" / "best.pt")
