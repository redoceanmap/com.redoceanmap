# 시멘틱 분할 (Semantic Segmentation) — 구현 지시서 (허브 비전 슬라이스)

> 원 과제: **PSPNet** (~2017). 이 문서는 그것을 RTX 3050(8GB) + 이 프로젝트 구조에 맞는
> 현대 대체 모델로 번역한 작업 명세다.
> 하네스 원칙·아키텍처 매핑은 [[minseok/apps/hub/_docs/image_classifier|image_classifier]] §1·§2를 그대로 따른다.

---

## 0. 대체 모델 추천

| | 원 모델 | 추천 | 근거 |
|---|---|---|---|
| 모델 | PSPNet (ResNet50) | **SegFormer-B0** (`nvidia/segformer-b0-finetuned-ade-512-512`) | 3.8M 파라미터로 PSPNet(~50M)보다 가볍고 mIoU 동급 이상. **transformers는 이미 requirements에 있다**(mail watcher KcELECTRA) — 신규 의존성 0개 |
| 파인튜닝 | 전층 재학습 | HF `Trainer` full FT — 3.8M이라 LoRA조차 불필요 | fp16, 512px, batch 8 → ~4GB. 커스텀 데이터셋은 `datasets`(darwin 로컬 보유)로 구성 |
| 대안 | — | torchvision `deeplabv3_mobilenet_v3_large` | transformers 없이 가려면. 다만 이미 있으므로 SegFormer가 기본 |

## 1. 슬라이스 파일 (1:1 — `apps/hub/` 기준)

```
adapter/inbound/api/schemas/semantic_segmenter_schema.py
adapter/inbound/api/v1/semantic_segmenter_router.py       # POST /vision/segmentations
app/dtos/semantic_segmenter_dto.py
app/ports/input/semantic_segmenter_use_case.py
app/ports/output/semantic_segmenter_port.py
app/use_cases/semantic_segmenter_interactor.py
adapter/outbound/resource_adapters/segformer/hf_segformer_adapter.py
dependencies/semantic_segmenter_provider.py               # @lru_cache 싱글턴
tests/app/use_cases/test_semantic_segmenter_interactor.py
```

## 2. 포트 계약 — 마스크가 아니라 "요약"이 계약이다

픽셀 마스크 원본(HxW 배열)을 HTTP로 나르면 응답이 수 MB가 된다. 계약은 **클래스별 점유 요약**으로
하고, 마스크 이미지는 기존 `VisionStoragePort`(S3)에 저장해 object_key만 답한다.

```python
@dataclass(frozen=True)
class SegmentSummary:
    label: str
    pixel_ratio: float        # 전체 대비 점유율 0~1, round(4)

class SemanticSegmenterPort(ABC):
    @abstractmethod
    def segment(self, image: bytes) -> tuple[list[SegmentSummary], bytes]:
        """(점유율 내림차순 요약, 컬러 마스크 PNG bytes)를 반환한다. 디코딩 불가는 UnreadableImageError."""
```

- 마스크 PNG 저장은 인터랙터가 `VisionStoragePort`로 위임(허브 소유 S3 인프라 재사용) —
  어댑터는 S3를 모른다.
- `VISION_S3_BUCKET` 미설정 시 저장 생략하고 `mask_object_key=None`(열화 동작 — 요약은 항상 반환).

## 3. 어댑터 요구사항

- `SegformerImageProcessor` + `SegformerForSemanticSegmentation.from_pretrained(config 모델명)`.
  전처리·라벨(`model.config.id2label`)은 모델 메타에서 유도 — 하드코딩 금지.
- `eval()` + `no_grad()`, cuda일 때만 `torch.autocast("cuda")`. 로짓을 원본 해상도로
  `interpolate(mode="bilinear")` 후 argmax — 이 업샘플은 결정적 후처리로 어댑터 소유.
- 워밍업 1회. 컬러 팔레트는 클래스 인덱스에서 결정적으로 생성(랜덤 금지 — 같은 클래스는 항상 같은 색).

## 4. 게이팅 (인터랙터 — 결정적)

분할의 신뢰 신호는 "지배 클래스가 얼마나 명확한가"다:

```
1위 pixel_ratio ≥ SEGMENT_DOMINANT (0.3)   → decision = "auto_accepted"
그 외 (파편화된 분할)                       → decision = "needs_review"
```

로그 1줄: `시멘틱 분할: file=%s, latency_ms=%d, top_label=%s, ratio=%.4f, decision=%s`.

## 5. 설정 (`core/config.py`)

```python
SEGMENT_MODEL = os.getenv("SEGMENT_MODEL", "nvidia/segformer-b0-finetuned-ade-512-512")
SEGMENT_DOMINANT = float(os.getenv("SEGMENT_DOMINANT", "0.3"))
```

## 6. 테스트 (모델 없이 스텁 포트)

1. 게이팅: 1위 ratio 0.6 → auto_accepted / 0.1 → needs_review / 정확히 0.3 → auto_accepted.
2. 저장 협력: 스텁 VisionStoragePort가 마스크 bytes를 받았고 object_key가 응답에 실리는지,
   버킷 미설정 스텁이면 mask_object_key=None에도 요약은 반환되는지.
3. 요약이 점유율 내림차순·round(4)인지.

## 7. RTX 3050 체크리스트 / 수용 기준

- [ ] 신규 의존성 0개(transformers 재사용). 모델 1회 로드 + 워밍업.
- [ ] 파인튜닝 시: fp16, 512px, batch 8, `Trainer` — 8GB 내. 데이터셋 라벨맵은 config json으로.
- [ ] 전처리·라벨이 모델 메타에서 유도(하드코딩 0개).
- [ ] 마스크는 S3, HTTP 응답은 요약만 — 응답 크기 상한이 이미지 크기와 무관.
- [ ] 게이팅 결정적 + 스텁 테스트 통과 + `lint-imports` KEPT.
