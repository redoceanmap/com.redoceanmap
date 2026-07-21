from __future__ import annotations

import io

import torch
from PIL import Image
from torchvision.models import ConvNeXt_Tiny_Weights, convnext_tiny

from hub.app.ports.output.image_classifier_port import ImageClassifierPort, UnreadableImageError


class TorchvisionConvnextAdapter(ImageClassifierPort):
    """torchvision ConvNeXt-Tiny 분류 엔진. 전처리·라벨은 weights 메타에서 유도(하드코딩 금지)."""

    def __init__(self, device: str = "auto") -> None:
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self._device = device
        weights = ConvNeXt_Tiny_Weights.IMAGENET1K_V1
        self._transform = weights.transforms()
        self._categories: list[str] = weights.meta["categories"]
        self._model = convnext_tiny(weights=weights).to(device).eval()
        self._infer(Image.new("RGB", (32, 32)))  # 워밍업 — 첫 실제 요청의 지연 제거

    def _infer(self, image: Image.Image) -> torch.Tensor:
        batch = self._transform(image).unsqueeze(0).to(self._device)
        with torch.no_grad(), torch.autocast("cuda", enabled=self._device == "cuda"):
            logits = self._model(batch)
        return logits.softmax(dim=1)[0].float().cpu()

    def classify(self, image: bytes, top_k: int) -> list[tuple[str, float]]:
        try:
            pil = Image.open(io.BytesIO(image)).convert("RGB")
        except OSError as exc:  # UnidentifiedImageError 포함
            raise UnreadableImageError(f"이미지 디코딩 실패: {exc}") from exc
        probs = self._infer(pil)
        top = torch.topk(probs, k=min(top_k, len(self._categories)))
        return [(self._categories[int(idx)], float(prob)) for prob, idx in zip(top.values, top.indices)]
