from __future__ import annotations

from pathlib import Path

from hub.app.ports.output.face_dataset_port import FaceDatasetPort


class LocalYoloDatasetAdapter(FaceDatasetPort):
    """로컬 디렉토리(resources/yolo_train)의 YOLO 포맷 데이터셋을 공급한다."""

    def __init__(self, base_path: Path) -> None:
        self._base_path = base_path

    def get_dataset_config_path(self) -> str:
        yaml_path = self._base_path / "data.yaml"
        if not yaml_path.exists():
            raise FileNotFoundError(f"YOLO data.yaml을 찾을 수 없습니다: {yaml_path}")
        return str(yaml_path.resolve())
