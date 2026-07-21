# 이미지 생성 (Image Generation) — 구현 지시서 (허브 비전 슬라이스)

> 원 과제: **DCGAN · Self-Attention GAN** (~2018). 이 문서는 그것을 RTX 3050(8GB) + 이 프로젝트
> 구조에 맞는 현대 대체 모델로 번역한 작업 명세다.
> 하네스 원칙·아키텍처 매핑은 [[minseok/apps/hub/_docs/image_classifier|image_classifier]] §1·§2를 그대로 따른다.

---

## 0. 대체 모델 추천 — GAN은 폐기한다

| | 원 모델 | 추천 | 근거 |
|---|---|---|---|
| 모델 | DCGAN / SAGAN | **Stable Diffusion 1.5** (diffusers, fp16) | GAN은 생성 품질·제어(텍스트 프롬프트)·학습 안정성 전부에서 확산 모델에 밀려 실무 폐기 수순. SD1.5는 fp16 추론 ~4GB로 8GB에 정확히 맞는 체급 |
| 파인튜닝 | GAN 재학습 (모드 붕괴와의 싸움) | **LoRA** (diffusers 학습 스크립트) | 512px, batch 1 + gradient accumulation, gradient checkpointing, 8bit Adam → ~6–7GB. 수백 장 데이터로 스타일/피사체 학습 가능 |
| 대안 | — | SDXL-Turbo (1~4 step 추론) | 지연이 중요하면. 단 LoRA 학습은 8GB에서 빠듯해 기본 채택하지 않음 |

**신규 의존성**: `diffusers`, `accelerate` (+ LoRA 학습 시 `peft`, `bitsandbytes` — 학습은
백엔드 PC(window)에서만, 컨테이너 제외 마커 검토).

## 1. VRAM 동거 경고 (이 슬라이스 특유의 제약)

SD1.5 상주(~4GB)는 ConvNeXt·YOLO 등 다른 비전 모델과 **동시 상주 시 8GB를 넘길 수 있다**.

- provider 싱글턴은 유지하되, config `IMAGE_GEN_ENABLED`(기본 false)로 **명시적 opt-in**일 때만
  로드한다 — 꺼져 있으면 라우터가 503(계약 예외 `ImageGenerationUnavailable` → 라우터 번역).
- 생성은 GPU 독점 작업이므로 인터랙터에서 `threading.Lock`으로 동시 1건 직렬화(결정적 배압).
  큐·워커 신설은 하지 않는다(Simplicity First — 필요해지면 그때).

## 2. 슬라이스 파일 (1:1 — `apps/hub/` 기준)

```
adapter/inbound/api/schemas/image_generator_schema.py
adapter/inbound/api/v1/image_generator_router.py          # POST /vision/generations
app/dtos/image_generator_dto.py
app/ports/input/image_generator_use_case.py
app/ports/output/image_generator_port.py                  # + ImageGenerationUnavailable
app/use_cases/image_generator_interactor.py
adapter/outbound/resource_adapters/diffusion/sd_image_generator_adapter.py
dependencies/image_generator_provider.py
tests/app/use_cases/test_image_generator_interactor.py
```

## 3. 포트 계약

```python
class ImageGeneratorPort(ABC):
    @abstractmethod
    def generate(self, prompt: str, negative_prompt: str, seed: int, steps: int) -> bytes:
        """프롬프트로 PNG bytes 1장을 생성한다. seed 고정 시 결과 재현(결정적 검증 가능)."""
```

- **seed는 필수 인자** — 라우터가 요청에 없으면 config 기본 seed를 쓴다. "같은 입력 → 같은 출력"이
  하네스 검증의 전제다(랜덤 기본값 금지).
- 생성물 저장은 인터랙터가 `VisionStoragePort`(S3)로 위임하고 object_key를 답한다 —
  응답 본문에 이미지 bytes를 싣지 않는다(semantic_segmenter와 동일 결정).

## 4. 어댑터 요구사항

- `StableDiffusionPipeline.from_pretrained(config 모델명, torch_dtype=float16)` + cuda.
  `enable_attention_slicing()`으로 VRAM 피크 완화. cpu 폴백은 **지원하지 않는다**(맥에서는
  IMAGE_GEN_ENABLED=false가 정상 상태 — 분류 계열과 달리 cpu 생성은 분 단위라 실용 불가).
- LoRA 가중치: config `IMAGE_GEN_LORA_PATH` 지정 시 `load_lora_weights()` — 없으면 베이스만.
- 프롬프트는 어댑터가 가공하지 않는다(프롬프트 엔지니어링은 소비자 몫 — 모델은 dumb).

## 5. 게이팅 (인터랙터 — 결정적)

생성은 신뢰도 점수가 없으므로 게이팅 대상은 **입력과 자원**이다:

```
IMAGE_GEN_ENABLED=false                → 503 ImageGenerationUnavailable
prompt 길이 0 또는 > IMAGE_GEN_MAX_PROMPT → 400 (라우터 검증)
Lock 획득 실패(동시 요청)               → 즉시 409 "생성 작업이 진행 중입니다" (대기 큐 없음)
```

로그 1줄: `이미지 생성: prompt_len=%d, steps=%d, seed=%d, latency_ms=%d, key=%s` (프롬프트 원문은 로깅 금지 — 길이만).

## 6. 설정 (`core/config.py`)

```python
IMAGE_GEN_ENABLED = os.getenv("IMAGE_GEN_ENABLED", "false").lower() == "true"
IMAGE_GEN_MODEL = os.getenv("IMAGE_GEN_MODEL", "runwayml/stable-diffusion-v1-5")
IMAGE_GEN_LORA_PATH = os.getenv("IMAGE_GEN_LORA_PATH", "")
IMAGE_GEN_STEPS = int(os.getenv("IMAGE_GEN_STEPS", "25"))
IMAGE_GEN_DEFAULT_SEED = int(os.getenv("IMAGE_GEN_DEFAULT_SEED", "42"))
IMAGE_GEN_MAX_PROMPT = int(os.getenv("IMAGE_GEN_MAX_PROMPT", "500"))
```

## 7. LoRA 파인튜닝 레시피 (RTX 3050 8GB — 백엔드 PC 전용)

diffusers 공식 `train_text_to_image_lora.py` 사용, 독립 스크립트로(`scripts/` — 서버 코드와 분리):

```
resolution=512, train_batch_size=1, gradient_accumulation_steps=4,
gradient_checkpointing, mixed_precision="fp16", use_8bit_adam, rank=8
```

산출 LoRA를 `IMAGE_GEN_LORA_PATH`로 지정하면 서버 코드 변경 없이 반영된다.

## 8. 테스트 (모델 없이 스텁 포트)

1. ENABLED=false 주입 시 인터랙터가 `ImageGenerationUnavailable`을 던지는지.
2. Lock 점유 상태에서 두 번째 호출이 대기 없이 충돌 신호를 반환하는지.
3. 스텁 생성 bytes가 VisionStoragePort 스텁에 전달되고 object_key가 응답에 실리는지.
4. seed 미지정 요청에 config 기본 seed가 포트로 전달되는지.

## 9. 수용 기준

- [ ] IMAGE_GEN_ENABLED opt-in 없이는 모델이 로드되지 않는다(맥에서 서버 기동에 영향 0).
- [ ] seed 고정 재현성이 계약에 명시되고 테스트로 고정된다.
- [ ] 동시 생성 직렬화(Lock)가 결정적으로 동작한다.
- [ ] 프롬프트 원문이 로그에 남지 않는다.
- [ ] LoRA 교체가 env 변경만으로 가능하다. `lint-imports` KEPT.
