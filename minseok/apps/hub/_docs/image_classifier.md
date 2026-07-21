# ConvNeXt-Tiny 이미지 분류 — 구현 지시서 (허브 비전 슬라이스)

> 이 문서는 에이전트(Claude Code 등)에게 주는 **작업 명세(spec)**다. 아래 구조·수용 기준을 그대로 따라 구현하라.
> 핵심 사상: **모델은 상태 없는(dumb) 컴포넌트**이고, 신뢰성은 그 주위를 감싸는 **결정적 하네스 코드**가 책임진다.
> 전처리·검증·신뢰도 게이팅·에스컬레이션·관측(로깅)은 모두 결정적 로직으로 구현하며, 모델의 판단에 맡기지 않는다.
>
> 원본은 독립 `convnext_agent/` 패키지 + Anthropic tool-calling 에이전트 명세였다. 본 문서는 그것을
> **이 프로젝트의 실제 구조** — 허브 소유 비전 기능(구 vision 스포크 흡수, YOLO와 동일 위상) +
> 헥사고날 수직 슬라이스 1:1 컨벤션 — 로 번역한 것이다. 달라진 결정과 근거는 §12에 모아뒀다.

---

## 0. 목표

백엔드 PC(RTX 3050, 8GB VRAM — `window` 브랜치 구동, 맥은 개발만)에서 동작하는
**ConvNeXt-Tiny 이미지 분류 수직 슬라이스**를 `apps/hub`에 만든다.

- HTTP 표면: `POST /vision/classifications` (이미지 업로드 → 분류 + 신뢰도 판정).
- 단순 분류기가 아니라, top-1 신뢰도에 따라 **자동 확정 / 재확인 필요 / 사람 확인 필요**를
  결정적 코드로 판정해 응답에 명시하는 게이팅 슬라이스다.

## 1. 하네스 엔지니어링 원칙 (반드시 준수)

구현 중 충돌이 생기면 이 원칙이 우선한다.

1. **모델과 하네스의 분리.** 모델(어댑터)은 `이미지 bytes → (라벨, 확률) 상위 k` 만 담당한다.
   그 외 전부(업로드 검증, 게이팅, 오류 응답, 로깅)는 인터랙터·라우터의 결정적 코드가 처리한다.
2. **결정적 스캐폴딩.** 게이팅·에스컬레이션에 "모델이 알아서" 하는 부분을 두지 않는다.
   모든 정책은 명시적 코드와 `core/config.py` 설정값으로 표현한다.
3. **명확한 계약.** 계층 간 연결은 타입이 명시된 포트(ABC)와 frozen dataclass DTO로 한다.
   유스케이스는 어댑터 스키마가 아니라 app DTO를 받는다(스키마↔DTO 변환은 라우터 몫).
4. **관측 가능성.** 모든 분류 호출은 지연시간(ms)·top-1 신뢰도·판정 결과를 로그로 남긴다.
   개인정보 보호를 위해 전체 경로가 아니라 **파일명만** 로깅한다.
5. **안전한 기본값과 에스컬레이션.** 신뢰도가 임계값 미만이면 자동 확정하지 않고,
   후보 목록과 함께 재확인/사람 확인 신호를 반환한다.
6. **테스트 가능성.** 게이팅·경계값·오류 처리는 **모델 로딩 없이** 스텁 포트로 검증한다.
7. **설정 주도.** 매직 넘버 금지. 임계값·top-k·디바이스는 `core/config.py`에서 읽는다.

## 2. 아키텍처 — 원본 3층의 헥사고날 매핑

| 원본 스펙 | 이 프로젝트 | 파일 |
|---|---|---|
| Layer 1: Model Service | 아웃바운드 리소스 어댑터 (YOLO의 `ultralytics_yolo_adapter` 패턴) | `adapter/outbound/resource_adapters/convnext/torchvision_convnext_adapter.py` |
| Layer 2: Skills + dispatch | 아웃바운드 포트(ABC) + 인터랙터(대장) | `app/ports/output/image_classifier_port.py` · `app/use_cases/image_classifier_interactor.py` |
| Layer 3: Agent (tool loop) | **만들지 않는다** — 에스컬레이션 3분기를 인터랙터의 결정적 코드로 구현 (§12-①) | 인터랙터 내 게이팅 |
| tool_schemas / dispatch | FastAPI 라우터 + pydantic 스키마 (HTTP가 곧 계약) | `adapter/inbound/api/v1/image_classifier_router.py` |
| observability.py | 기존 `logging` 패턴 (별도 모듈 금지, §8) | 인터랙터 내 logger |
| config.py | `core/config.py`에 env 기반 상수 추가 | `CONVNEXT_*` |

의존 방향은 앱 공통 규칙 그대로: `adapter → app → domain`, 상위가 하위 내부를 모른다
(라우터가 텐서를 만지면 안 되고, 어댑터가 게이팅 정책을 알면 안 된다).

## 3. 생성할 파일 (수직 슬라이스 1:1 — 전부 `apps/hub/` 기준)

```
adapter/inbound/api/schemas/image_classifier_schema.py    # 요청/응답 pydantic 스키마
adapter/inbound/api/v1/image_classifier_router.py         # POST /vision/classifications
app/dtos/image_classifier_dto.py                          # Command·Candidate·Response (frozen dataclass)
app/ports/input/image_classifier_use_case.py              # ImageClassifierUseCase (ABC)
app/ports/output/image_classifier_port.py                 # ImageClassifierPort (ABC) — 모델 엔진 계약
app/use_cases/image_classifier_interactor.py              # 대장 — 게이팅·에스컬레이션·로깅 (빈 파일 존재)
adapter/outbound/resource_adapters/convnext/
└── torchvision_convnext_adapter.py                       # ConvNeXt-Tiny 로딩·전처리·추론
dependencies/image_classifier_provider.py                 # DI — lru_cache 싱글턴 (모델 1회 로드)
tests/app/use_cases/test_image_classifier_interactor.py   # 스텁 포트로 게이팅 경계 검증
```

배선(수정):

- `main.py` — `app.include_router(image_classifier_router, dependencies=_authenticated)`.
- `hub/_docs/CLAUDE.md` — 인바운드 라우터 표 `/vision/*` 행에 `image_classifier`(/classifications) 추가.
- `vision_router`의 `/myself` 소개문에 분류 기능 한 줄 추가
  (새 라우터는 기존 `/vision` prefix 아래 슬라이스이므로 `face_recognition_router`처럼 자체 `/myself`는 만들지 않는다).
- `requirements.txt` — **추가 없음** (§12-②: torchvision 기본 채택, timm 도입 안 함).

## 4. 모델 어댑터 (`torchvision_convnext_adapter.py`)

`ImageClassifierPort` 구현. `UltralyticsYoloAdapter`와 같은 위상의 리소스 어댑터다.

- `torchvision.models.convnext_tiny(weights=ConvNeXt_Tiny_Weights.IMAGENET1K_V1)`로 로드한다.
- **전처리 하드코딩 금지.** `weights.transforms()`가 주는 전처리를 그대로 쓴다
  (원본 스펙의 `resolve_data_config`와 같은 목적 — 학습/추론 전처리 불일치는 조용한 정확도 붕괴의 주원인).
- **라벨 하드코딩·labels.json 금지.** `weights.meta["categories"]`가 클래스 라벨 원천이다.
- 디바이스: config `CONVNEXT_DEVICE="auto"`면 `cuda 가용 시 cuda, 아니면 cpu`
  (맥 개발 환경은 cpu로 자연 폴백 — 백엔드 PC에서만 cuda).
- 추론: `model.eval()` + `torch.no_grad()` 상시. cuda일 때만 `torch.autocast("cuda")`(AMP)로
  속도↑·VRAM↓ (RTX 3050 8GB 대응). softmax 확률은 `float().cpu()`로 내린다.
- **워밍업**: `__init__`에서 더미 텐서 1회 추론 — 첫 실제 요청의 지연 제거.
- 계약(포트 시그니처, YoloPort.predict와 같은 모양):

  ```python
  class ImageClassifierPort(ABC):
      @abstractmethod
      def classify(self, image: bytes, top_k: int) -> list[tuple[str, float]]:
          """이미지에서 (라벨, softmax 확률) 상위 top_k를 확률 내림차순으로 반환한다.
          디코딩 불가 이미지는 UnreadableImageError를 던진다."""
  ```

- 이 어댑터는 파일 I/O 경로·게이팅 정책·HTTP를 몰라야 한다. 입력은 bytes, 출력은 (라벨, 확률) 목록뿐.
- 디코딩 실패는 어댑터가 `UnreadableImageError`(포트 파일에 정의한 계약 예외 — `StockAnalysisUnavailable` 패턴)로
  알리고, 라우터가 400으로 번역한다. RGB 변환(`Image.convert("RGB")`)은 어댑터 책임.

**top-k 재호출 금지**: 확률 벡터는 1회 추론에서 전부 나온다. 원본 스펙의
`classify_image` / `classify_topk` 2회 호출 설계는 낭비 — 포트가 처음부터 상위 k를 반환하고,
top-1 확정이든 후보 제시든 인터랙터가 그 한 결과로 판정한다.

## 5. 인터랙터 (`image_classifier_interactor.py`) — 게이팅의 소유자

`ImageClassifierUseCase` 구현. 에스컬레이션 3분기를 **결정적 코드로 강제**한다(LLM 개입 없음).

```
top-1 ≥ CONVNEXT_HIGH_CONFIDENCE            → decision = "auto_accepted"   (자동 확정)
LOW ≤ top-1 < HIGH                          → decision = "needs_review"    (후보 목록으로 재확인)
top-1 < CONVNEXT_LOW_CONFIDENCE             → decision = "human_required"  (자동 처리 금지)
```

- 경계는 **이상(≥)** 으로 통일한다: 정확히 HIGH면 auto_accepted, 정확히 LOW면 needs_review.
  테스트가 이 경계를 고정한다(§9).
- 어떤 분기든 상위 k 후보 전체를 응답에 동봉한다 — 소비자(프론트/운영자)가 재확인 근거로 쓴다.
- DTO (`app/dtos/image_classifier_dto.py`, 전부 frozen dataclass):

  ```python
  ImageClassificationCommand(filename: str, content: bytes)
  ClassificationCandidate(label: str, confidence: float)      # confidence는 round(4)
  ImageClassificationResponse(filename: str, decision: str,
                              candidates: tuple[ClassificationCandidate, ...])
  ```

- 로깅(§8)은 인터랙터가 수행한다 — 어댑터·라우터에 중복하지 않는다.

## 6. 라우터 (`image_classifier_router.py`)

`face_recognition_router` 패턴을 그대로 따른다.

- `POST /vision/classifications` — `UploadFile` 수신.
- 결정적 입력 검증은 라우터 몫: `content_type`이 `image/*`가 아니면 400
  (기존 문구 재사용: "이미지 파일만 업로드할 수 있습니다.").
- 추론은 CPU-bound sync이므로 `await asyncio.to_thread(...)`로 이벤트 루프를 막지 않는다.
- `UnreadableImageError` → `HTTPException(400, "이미지를 해석할 수 없습니다.")`.
  그 외 예외는 삼키지 않는다(전역 핸들러 몫).
- 스키마↔DTO 변환은 여기서만 한다.

## 7. 설정 (`core/config.py`에 추가)

기존 `os.getenv` 패턴 그대로. 코드 어디에도 같은 숫자를 중복 하드코딩하지 않는다.

```python
# ---- 비전 / ConvNeXt 이미지 분류 (hub — 신뢰도 게이팅 임계값) ----
CONVNEXT_DEVICE = os.getenv("CONVNEXT_DEVICE", "auto")            # "auto" | "cuda" | "cpu"
CONVNEXT_HIGH_CONFIDENCE = float(os.getenv("CONVNEXT_HIGH_CONFIDENCE", "0.85"))  # 이상이면 자동 확정
CONVNEXT_LOW_CONFIDENCE = float(os.getenv("CONVNEXT_LOW_CONFIDENCE", "0.55"))    # 미만이면 사람 확인
CONVNEXT_TOP_K = int(os.getenv("CONVNEXT_TOP_K", "5"))
```

임계값은 **provider가 읽어 인터랙터 생성자로 주입**한다 — 인터랙터가 config를 직접 import하면
테스트에서 경계값을 주입할 수 없다.

## 8. 관측 가능성

별도 `observability.py` 모듈은 만들지 않는다(단일 슬라이스에 과설계 — Simplicity First).
기존 `logging` 컨벤션(`log_vision_record_adapter`·`face_recognition_interactor` 참고)으로,
인터랙터가 분류 1건당 1줄을 남긴다:

```python
logger.info("이미지 분류: file=%s, latency_ms=%d, top1=%.4f, decision=%s",
            command.filename, latency_ms, top1, decision)
```

- 파일명만 로깅한다(전체 경로·이미지 내용 금지).
- 지연시간은 인터랙터에서 `time.perf_counter()`로 포트 호출을 감싸 측정한다.
- JSONL 파일 분리·수집이 필요해지면 그때 핸들러 설정으로 해결한다(코드 변경 없이).

## 9. 테스트 (`tests/app/use_cases/test_image_classifier_interactor.py`)

**모델을 로딩하지 않는다.** 고정 확률을 반환하는 `_StubClassifierPort`를 주입해 검증한다
(기존 `_StubYoloPort` 스타일, 테스트명은 한국어).

필수 케이스:

1. 게이팅 3분기 — top-1이 HIGH 이상 / LOW~HIGH 사이 / LOW 미만일 때 decision이 각각
   `auto_accepted` / `needs_review` / `human_required`.
2. 경계값 — top-1이 **정확히** HIGH일 때 auto_accepted, **정확히** LOW일 때 needs_review
   (임계값은 생성자 주입으로 테스트가 직접 지정).
3. 포트 계약 — 스텁이 받은 `top_k` 인자가 주입한 설정값과 일치, 후보가 확률 내림차순으로
   round(4) 되어 응답에 그대로 실리는지.
4. 라우터 검증(선택, TestClient) — `image/*`가 아닌 업로드에 400.

실행: `minseok/`에서 `PYTHONPATH=apps pytest apps/hub/tests/app/use_cases/test_image_classifier_interactor.py`
+ `lint-imports` (허브 격리 계약 위반 없음 확인).

## 10. RTX 3050 (8GB) 체크리스트

- [ ] 모델은 **프로세스당 1회만** 로드 — provider `@lru_cache(maxsize=1)` 싱글턴
      (`face_recognition_provider` 패턴). 매 요청 로딩 금지.
- [ ] `eval()` + `no_grad()` 상시, cuda일 때만 AMP(`torch.autocast`).
- [ ] 전처리·라벨은 torchvision weights 메타에서 유도 — 하드코딩 정규화 값 0개.
- [ ] 워밍업 1회로 첫 요청 지연 제거.
- [ ] 맥(개발)에서는 cpu 폴백으로 동일 코드가 그대로 돈다.
- [ ] 배치 추론·해상도 조절은 **만들지 않는다** — 요청이 몰리는 실사용이 생기면 그때 추가(§12-③).

## 11. 수용 기준 (Definition of Done)

- [ ] §3의 슬라이스 파일 9개가 모두 존재하고 `adapter → app` 단방향 의존만 있다(`lint-imports` 통과).
- [ ] 모델은 프로세스당 1회 로드 + 워밍업 동작.
- [ ] 전처리·라벨이 `ConvNeXt_Tiny_Weights` 메타에서 유도되고 하드코딩 값이 없다.
- [ ] 게이팅 3분기가 인터랙터의 결정적 코드로 구현되고 임계값은 생성자 주입이다.
- [ ] 디코딩 불가 이미지가 500이 아니라 400으로 응답된다.
- [ ] 분류 1건당 지연시간·top-1·decision이 로그 1줄로 남는다(파일명만).
- [ ] 모델 없이 스텁 포트로 §9 테스트가 전부 통과한다.
- [ ] 조정 가능한 값이 전부 `core/config.py`의 `CONVNEXT_*`에 모여 있다.
- [ ] `main.py` 배선 + hub CLAUDE 라우터 표 + vision `/myself` 소개문이 갱신됐다.

## 12. 원본 스펙에서 달라진 결정 (근거)

| # | 원본 | 변경 | 근거 |
|---|---|---|---|
| ① | Layer 3: Anthropic Messages API tool-calling 에이전트 루프 | **제외.** 게이팅·에스컬레이션은 인터랙터의 결정적 코드 | 원본 스스로 "분기는 LLM에 맡기지 말라"고 했다 — 그러면 도구를 고를 LLM이 할 일이 없다. 프로젝트는 단일 LLM 정책(EXAONE 7.8B, `core/llm/llm_orchestrator.py` 수렴)이라 Anthropic API 도입은 정책 위반. 대화형 소비가 필요해지면 chat이 허브 포트를 소비하는 기존 패턴으로 잇는다 |
| ② | `timm.create_model` + `resolve_data_config` + labels.json | torchvision `convnext_tiny` + weights 메타 | torch/torchvision은 이미 requirements에 있고 timm은 없다. 신규 의존성 0개로 같은 보장(전처리·라벨을 모델 메타에서 유도)을 얻는다. 커스텀 파인튜닝 체크포인트가 생기면 포트 계약은 그대로 두고 어댑터만 timm 구현으로 교체 |
| ③ | `predict_batch`·해상도/배치 config | 제외 | 호출자가 없는 투기적 기능(Simplicity First). 필요 시점에 포트 메서드 추가 |
| ④ | 도구가 `{"ok": false, ...}` dict 반환 | 계약 예외 + HTTP 상태코드 | dict 오류 계약은 LLM tool-loop 전제였다. HTTP 세계의 등가물은 pydantic 스키마 + 400/422이고, 계약 예외(`UnreadableImageError`)는 허브의 기존 관례(`StockAnalysisUnavailable`) |
| ⑤ | `observability.py` + JSONL 파일 | 표준 `logging` 1줄 | 프로젝트 전체가 logging 컨벤션. 필드(지연시간·신뢰도·판정)는 동일하게 남긴다 |
| ⑥ | 독립 `convnext_agent/` 디렉토리 | hub 수직 슬라이스 | 비전은 허브 소유 기능(구 vision 스포크 흡수). YOLO와 같은 위상으로 스타 토폴로지·1:1 컨벤션에 편입 |

## 13. 구현 순서 (권장)

1. `core/config.py`에 `CONVNEXT_*` 추가 → verify: import 확인
2. 포트 2개(input UseCase·output ClassifierPort) + DTO — **계약 먼저 고정**
3. 인터랙터 + 테스트(스텁 포트) → verify: `PYTHONPATH=apps pytest` 통과
4. torchvision 어댑터(워밍업·AMP·디코딩 예외) → verify: 로컬 1회 수동 추론
5. 스키마 + 라우터 + provider + `main.py` 배선 → verify: `/vision/classifications` 수동 호출
6. hub CLAUDE 라우터 표 + vision `/myself` 갱신 → verify: `lint-imports` 통과
