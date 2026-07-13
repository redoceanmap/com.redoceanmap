from dataclasses import dataclass


@dataclass(frozen=True)
class FaceTrainingCommand:

    base_weights: str = "yolo11n.pt"
    epochs: int = 50
    batch_size: int = 16
    image_size: int = 640
    device: str = "cpu"  # Apple Silicon 로컬은 "mps", CUDA는 "0"


@dataclass(frozen=True)
class FaceTrainingResponse:

    dataset_config: str
    epochs: int
    save_dir: str
    best_weights: str
