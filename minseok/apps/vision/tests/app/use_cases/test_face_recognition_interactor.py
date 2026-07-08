from vision.app.dtos.face_recognition_dto import FaceRecognitionCommand
from vision.app.use_cases.face_recognition_interactor import FaceRecognitionInteractor


class _StubYoloPort:
    def __init__(self):
        self.predict_kwargs = None

    def predict(self, **kwargs):
        self.predict_kwargs = kwargs
        return [("민석", 0.91234), ("face", 0.4)]


def test_인식은_주입된_가중치로_탐지하고_클래스_이름을_답한다():
    yolo = _StubYoloPort()

    result = FaceRecognitionInteractor(yolo=yolo, weights="runs/detect/train/weights/best.pt").recognize(
        FaceRecognitionCommand(filename="me.jpg", content=b"\x89PNG")
    )

    assert yolo.predict_kwargs["base_weights"] == "runs/detect/train/weights/best.pt"
    assert yolo.predict_kwargs["image"] == b"\x89PNG"
    assert result.filename == "me.jpg"
    assert result.matches[0].name == "민석"
    assert result.matches[0].confidence == 0.9123
    assert result.matches[1].name == "face"
