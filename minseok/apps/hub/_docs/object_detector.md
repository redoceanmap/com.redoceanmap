# 물체 감지 (Object Detection) — 구현 지시서 (허브 비전 슬라이스)

> 원 과제: **SSD** (Single Shot Detector, ~2016). 이 문서는 그것을 RTX 3050(8GB) + 이 프로젝트
> 구조에 맞는 현대 대체 모델로 번역한 작업 명세다.
> 하네스 원칙·아키텍처 매핑·구현 방식은 [[minseok/apps/hub/_docs/image_classifier|image_classifier]]
> §1·§2를 그대로 따른다 — 모델은 dumb 컴포넌트, 검증·게이팅·로깅은 결정적 하네스 코드.

---

## 0. 대체 모델 추천

| | 원 모델 | 추천 | 근거 |
|---|---|---|---|
| 모델 | SSD300 (VGG16 백본) | **YOLO11s** (ultralytics) | mAP·속도 모두 SSD를 압도. **ultralytics는 이미 requirements에 있고 허브에 어댑터 패턴(`UltralyticsYoloAdapter`)까지 있다** — 신규 의존성 0개 |
| 파인튜닝 | 전층 재학습 | ultralytics `train()` (기존 `FaceTrainingInteractor`와 동일 경로) | RTX 3050에서 `yolo11s`, imgsz 640, batch 16 무난 (~5GB) |
| 대안 | — | RT-DETR-L (동일 ultralytics) | NMS-free가 필요할 때. 8GB에선 학습이 빠듯하므로 기본 채택하지 않음 |

## 1. 기존 자산과의 관계 (중요)

허브에는 이미 YOLO 슬라이스(얼굴 인식·파인튜닝)가 있다. **이 슬라이스는 범용 물체 감지**로,
기존 것을 수정하지 않고 새 수직 슬라이스를 추가한다:

- `YoloPort.predict`는 (클래스, 신뢰도)만 반환 — 물체 감지는 **바운딩 박스가 필수**이므로
  포트를 재사용하지 않고 새 포트를 만든다(기존 얼굴 슬라이스는 건드리지 않는다 — Surgical Changes).
- 엔진 구현체(`ultralytics.YOLO`) 로딩 패턴은 `UltralyticsYoloAdapter`를 참고하되 클래스는 분리.

## 2. 슬라이스 파일 (1:1 — `apps/hub/` 기준)

```
adapter/inbound/api/schemas/object_detector_schema.py
adapter/inbound/api/v1/object_detector_router.py          # POST /vision/detections
app/dtos/object_detector_dto.py                           # Command·Detection·Response (frozen)
app/ports/input/object_detector_use_case.py
app/ports/output/object_detector_port.py                  # + UnreadableImageError는 image_classifier_port 것 재사용
app/use_cases/object_detector_interactor.py
adapter/outbound/resource_adapters/yolo/ultralytics_object_detector_adapter.py
dependencies/object_detector_provider.py                  # @lru_cache 싱글턴
tests/app/use_cases/test_object_detector_interactor.py
```

배선: `main.py` include_router + hub CLAUDE 라우터 표 `/vision/*` 행에 `object_detector`(/detections) 추가.

## 3. 포트 계약

```python
@dataclass(frozen=True)
class DetectedObject:
    label: str
    confidence: float          # round(4)
    box: tuple[float, float, float, float]   # xyxy, 픽셀 좌표

class ObjectDetectorPort(ABC):
    @abstractmethod
    def detect(self, image: bytes, min_confidence: float) -> list[DetectedObject]:
        """min_confidence 이상의 탐지를 신뢰도 내림차순으로 반환한다. NMS는 엔진 내장(결정적).
        디코딩 불가는 UnreadableImageError."""
```

## 4. 어댑터 요구사항

- 가중치: config `OBJECT_DETECT_WEIGHTS`(기본 `"yolo11s.pt"` — COCO 80클래스 사전학습,
  최초 실행 시 자동 다운로드). 파인튜닝 산출물 경로로 교체 가능.
- `conf=min_confidence`를 ultralytics 호출에 그대로 전달(후처리 임계값 중복 구현 금지).
- 디바이스는 ultralytics 자동 선택에 맡긴다(cuda 가용 시 cuda). 모델은 provider 싱글턴으로 1회 로드.
- 커스텀 클래스 파인튜닝이 필요하면 기존 `FaceTrainingInteractor` 경로(YOLO 데이터셋 yaml)를
  재사용한다 — 학습 슬라이스를 새로 만들지 않는다.

## 5. 게이팅 (인터랙터 — 결정적)

분류와 달리 탐지는 "몇 개를 얼마나 확신하며 찾았나"가 판정 대상이다:

```
탐지 0건                                   → decision = "nothing_found"
최고 신뢰도 ≥ OBJECT_DETECT_HIGH (0.6)     → decision = "auto_accepted"
그 외 (임계 이상 탐지는 있으나 모두 저신뢰)  → decision = "needs_review"
```

로그 1줄: `물체 감지: file=%s, latency_ms=%d, count=%d, top1=%.4f, decision=%s` (파일명만).

## 6. 설정 (`core/config.py`)

```python
OBJECT_DETECT_WEIGHTS = os.getenv("OBJECT_DETECT_WEIGHTS", "yolo11s.pt")
OBJECT_DETECT_MIN_CONFIDENCE = float(os.getenv("OBJECT_DETECT_MIN_CONFIDENCE", "0.25"))
OBJECT_DETECT_HIGH = float(os.getenv("OBJECT_DETECT_HIGH", "0.6"))
```

임계값은 provider가 읽어 인터랙터 생성자로 주입(테스트 주입 가능성).

## 7. 테스트 (모델 없이 스텁 포트)

1. 3분기: 0건 → nothing_found / 최고 0.9 → auto_accepted / 최고 0.4 → needs_review.
2. 경계값: 최고 신뢰도가 정확히 HIGH일 때 auto_accepted(≥ 통일).
3. 포트 계약: `min_confidence` 전달값, box 4튜플·round(4)가 응답에 그대로 실리는지.

## 8. RTX 3050 체크리스트 / 수용 기준

- [ ] 신규 의존성 0개 (ultralytics 재사용), 모델 프로세스당 1회 로드.
- [ ] 파인튜닝 시: `yolo11s`, imgsz 640, batch 16, AMP는 ultralytics 기본 — 8GB 내 동작.
- [ ] NMS·conf 필터가 엔진 1곳에만 존재(중복 구현 없음).
- [ ] 게이팅 3분기 결정적 코드 + 스텁 테스트 통과 + `lint-imports` KEPT.
- [ ] 기존 얼굴 인식 슬라이스(YoloPort·face_recognition)는 한 줄도 변경되지 않았다.
