# 동영상 분류 (Video Classification) — 구현 지시서 (허브 비전 슬라이스)

> 원 과제: **3DCNN · ECO** (~2018). 이 문서는 그것을 RTX 3050(8GB) + 이 프로젝트 구조에 맞는
> 현대 대체 모델로 번역한 작업 명세다. 사용자가 지정한 **QLoRA/LoRA 파인튜닝 대상 슬라이스**다.
> 하네스 원칙·아키텍처 매핑은 [[minseok/apps/hub/_docs/image_classifier|image_classifier]] §1·§2를 그대로 따른다.

---

## 0. 대체 모델 추천

| | 원 모델 | 추천 | 근거 |
|---|---|---|---|
| 모델 | 3DCNN (C3D 계열) / ECO | **VideoMAE-Base** (`MCG-NJU/videomae-base-finetuned-kinetics`, 86M) | 3D 합성곱 대비 파라미터 효율·정확도(Kinetics-400 top-1 ~80%) 압도. ViT 기반이라 **PEFT(LoRA) 파인튜닝이 정석으로 적용**된다. transformers 이미 보유 |
| 프레임 추출 | 자체 로더 | OpenCV 균일 샘플링 16프레임 | opencv 이미 보유. 샘플링 인덱스는 결정적 공식(균일 간격)으로 — 랜덤 샘플링은 학습 시에만 |
| 대안 | — | X3D-S (경량, torchvision) | 엣지 급 지연이 필요할 때. 파인튜닝 생태계(PEFT)가 VideoMAE 쪽이 좋아 기본 채택하지 않음 |

## 1. QLoRA에 대한 정직한 판정

**QLoRA(4bit 양자화 베이스 + LoRA)는 수십억 파라미터 LLM을 위한 기법**이다. VideoMAE-Base는
86M — fp16로 통째 올려도 ~0.2GB라 4bit 양자화로 아낄 VRAM이 없다. 8GB에서의 올바른 선택:

| 방식 | VRAM(학습) | 판정 |
|---|---|---|
| full FT (fp16, batch 2, grad accum 8, grad ckpt) | ~6GB | 가능 — 데이터 많을 때 |
| **LoRA (peft, r=16, q/v 프로젝션만)** | **~4GB** | **기본 채택** — 데이터 수백~수천 클립이면 충분, 산출물이 수 MB라 배포·롤백 쉬움 |
| QLoRA (bitsandbytes 4bit + LoRA) | ~3.5GB | 동작은 하나 이 체급에선 이득 없이 정밀도 위험만 추가 — 채택 안 함 |

**신규 의존성**: `peft` (학습 시), `av` 또는 opencv 재사용(디코딩 — opencv 기본).

## 2. 슬라이스 파일 (1:1 — `apps/hub/` 기준)

```
adapter/inbound/api/schemas/video_classifier_schema.py
adapter/inbound/api/v1/video_classifier_router.py         # POST /vision/video-classifications
app/dtos/video_classifier_dto.py
app/ports/input/video_classifier_use_case.py
app/ports/output/video_classifier_port.py                 # + UnreadableVideoError
app/use_cases/video_classifier_interactor.py
adapter/outbound/resource_adapters/videomae/hf_videomae_adapter.py
dependencies/video_classifier_provider.py                 # @lru_cache 싱글턴
scripts/finetune_video_classifier.py                      # LoRA 학습 (서버 코드와 분리)
tests/app/use_cases/test_video_classifier_interactor.py
```

## 3. 포트 계약

```python
class VideoClassifierPort(ABC):
    @abstractmethod
    def classify(self, video: bytes, top_k: int) -> list[tuple[str, float]]:
        """동영상에서 (행동 라벨, softmax 확률) 상위 top_k를 확률 내림차순으로 반환한다.
        디코딩 불가·프레임 부족은 UnreadableVideoError."""
```

image_classifier의 포트와 같은 모양 — 미래의 멀티에이전트 오케스트레이터가 두 도구를
동일한 계약 형태로 소비할 수 있다.

## 4. 어댑터 요구사항

- `VideoMAEImageProcessor` + `VideoMAEForVideoClassification.from_pretrained(config 모델명)`.
  전처리·라벨(id2label)은 모델 메타에서 유도 — 하드코딩 금지.
- 프레임 샘플링(결정적): 총 프레임 N에서 `linspace(0, N-1, 16)` 인덱스 16장 — opencv로 디코딩.
  N < 16이면 마지막 프레임 반복 패딩(공식을 docstring에 명시).
- `eval()` + `no_grad()`, cuda일 때만 AMP. 워밍업 1회(더미 16프레임).
- LoRA 산출물: config `VIDEO_CLS_LORA_PATH` 지정 시 `PeftModel.from_pretrained`로 병합 로드.

## 5. 라우터·게이팅

- 업로드 검증(라우터): `video/*` content_type 아니면 400,
  `VIDEO_CLS_MAX_MB`(50) 초과 413. 추론은 `asyncio.to_thread`.
- 게이팅(인터랙터 — image_classifier와 동일 3분기, 임계값만 별도 config):

```
top-1 ≥ VIDEO_CLS_HIGH (0.7)   → auto_accepted     # 행동 분류는 클래스 간 유사성이 커 0.85보다 낮게 시작
≥ VIDEO_CLS_LOW (0.4)          → needs_review
미만                            → human_required
```

- 로그 1줄: `동영상 분류: file=%s, latency_ms=%d, top1=%.4f, decision=%s` (파일명만).

## 6. 설정 (`core/config.py`)

```python
VIDEO_CLS_MODEL = os.getenv("VIDEO_CLS_MODEL", "MCG-NJU/videomae-base-finetuned-kinetics")
VIDEO_CLS_LORA_PATH = os.getenv("VIDEO_CLS_LORA_PATH", "")
VIDEO_CLS_HIGH = float(os.getenv("VIDEO_CLS_HIGH", "0.7"))
VIDEO_CLS_LOW = float(os.getenv("VIDEO_CLS_LOW", "0.4"))
VIDEO_CLS_TOP_K = int(os.getenv("VIDEO_CLS_TOP_K", "5"))
VIDEO_CLS_MAX_MB = int(os.getenv("VIDEO_CLS_MAX_MB", "50"))
```

## 7. LoRA 파인튜닝 레시피 (RTX 3050 8GB — 백엔드 PC 전용)

`scripts/finetune_video_classifier.py` (독립 스크립트, HF Trainer + peft):

```
base=MCG-NJU/videomae-base, LoRA r=16, alpha=32, target=["query","value"],
fp16, per_device_train_batch_size=2, gradient_accumulation_steps=8,
gradient_checkpointing, num_frames=16, lr=5e-4(LoRA만), epochs=5
```

- 학습 시 프레임 샘플링은 랜덤 클립, **추론은 균일 16프레임** — 두 정책이 다름을 코드에 명시.
- 커스텀 클래스 수가 다르면 분류 헤드는 새로 초기화(LoRA 대상 아님, full 학습).
- 산출 LoRA를 `VIDEO_CLS_LORA_PATH`로 지정 — 서버 코드 변경 없이 반영·롤백.

## 8. 테스트 (모델 없이 스텁 포트)

1. 3분기 + 경계값(정확히 0.7/0.4 → 상위 분기, ≥ 통일).
2. top_k 전달·round(4)·확률 내림차순.
3. `UnreadableVideoError` 스텁 → 인터랙터가 삼키지 않고 전파(라우터 400 번역은 통합에서).
4. (어댑터 단위, 모델 mock) 샘플링 공식: N=100 → linspace 인덱스 고정값, N=7 → 패딩 규칙.

## 9. 수용 기준

- [ ] LoRA 채택 근거(§1 표)가 유지되고 QLoRA 코드는 들어가지 않는다.
- [ ] 프레임 샘플링이 결정적 공식으로 문서화·테스트된다.
- [ ] 전처리·라벨이 모델 메타에서 유도(하드코딩 0개), 모델 1회 로드 + 워밍업.
- [ ] LoRA 교체·롤백이 env 변경만으로 가능하다.
- [ ] 스텁 테스트 통과 + `lint-imports` KEPT.
