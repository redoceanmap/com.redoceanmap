# 자세 추정 (Pose Estimation) — 구현 지시서 (허브 비전 슬라이스)

> 원 과제: **OpenPose** (~2017, Caffe 계열·무거움·라이선스 제약). 이 문서는 그것을
> RTX 3050(8GB) + 이 프로젝트 구조에 맞는 현대 대체 모델로 번역한 작업 명세다.
> 하네스 원칙·아키텍처 매핑은 [[minseok/apps/hub/_docs/image_classifier|image_classifier]] §1·§2를 그대로 따른다.

---

## 0. 대체 모델 추천

| | 원 모델 | 추천 | 근거 |
|---|---|---|---|
| 모델 | OpenPose (VGG19 백본, PAF) | **YOLO11s-pose** (ultralytics) | COCO 17 키포인트, 사람 탐지+자세를 단일 패스로. OpenPose 대비 수십 배 빠르고 상용 라이선스 문제 없음. **ultralytics 재사용 — 신규 의존성 0개** |
| 파인튜닝 | 사실상 불가 수준 | ultralytics `train()` (pose 데이터셋 yaml) | RTX 3050에서 imgsz 640, batch 16 무난 |
| 대안 | — | RTMPose (mmpose) | 정밀도가 더 필요할 때. mmcv 의존성 사슬이 무거워 기본 채택하지 않음 |

## 1. 슬라이스 파일 (1:1 — `apps/hub/` 기준)

```
adapter/inbound/api/schemas/pose_estimator_schema.py
adapter/inbound/api/v1/pose_estimator_router.py           # POST /vision/poses
app/dtos/pose_estimator_dto.py
app/ports/input/pose_estimator_use_case.py
app/ports/output/pose_estimator_port.py
app/use_cases/pose_estimator_interactor.py
adapter/outbound/resource_adapters/yolo/ultralytics_pose_adapter.py
dependencies/pose_estimator_provider.py                   # @lru_cache 싱글턴
tests/app/use_cases/test_pose_estimator_interactor.py
```

## 2. 포트 계약

```python
@dataclass(frozen=True)
class Keypoint:
    name: str                  # COCO 17 이름 (nose, left_eye, ...) — 모델 메타에서 유도
    x: float
    y: float
    confidence: float          # round(4)

@dataclass(frozen=True)
class DetectedPerson:
    box_confidence: float      # 사람 박스 신뢰도
    keypoints: tuple[Keypoint, ...]

class PoseEstimatorPort(ABC):
    @abstractmethod
    def estimate(self, image: bytes) -> list[DetectedPerson]:
        """사람별 17 키포인트를 박스 신뢰도 내림차순으로 반환한다. 디코딩 불가는 UnreadableImageError."""
```

## 3. 어댑터 요구사항

- 가중치: config `POSE_WEIGHTS`(기본 `"yolo11s-pose.pt"`, 자동 다운로드). provider 싱글턴 1회 로드.
- 키포인트 좌표는 **원본 픽셀 좌표**로 반환(정규화 좌표를 섞지 않는다 — 계약에 단위 명시).
- COCO 17 키포인트 이름 순서는 어댑터 상수 튜플 1곳에만 정의한다.

## 4. 게이팅 (인터랙터 — 결정적)

```
사람 0명                                        → decision = "nothing_found"
1위 박스 신뢰도 ≥ POSE_HIGH (0.7) 이고
  키포인트 평균 신뢰도 ≥ POSE_KEYPOINT_MIN (0.5) → decision = "auto_accepted"
그 외                                           → decision = "needs_review"  (가림/절단 의심)
```

로그 1줄: `자세 추정: file=%s, latency_ms=%d, persons=%d, top_box=%.4f, decision=%s`.

## 5. 설정 (`core/config.py`)

```python
POSE_WEIGHTS = os.getenv("POSE_WEIGHTS", "yolo11s-pose.pt")
POSE_HIGH = float(os.getenv("POSE_HIGH", "0.7"))
POSE_KEYPOINT_MIN = float(os.getenv("POSE_KEYPOINT_MIN", "0.5"))
```

## 6. 테스트 (모델 없이 스텁 포트)

1. 3분기: 0명 → nothing_found / 박스 0.9·키포인트 평균 0.8 → auto_accepted /
   박스 0.9·키포인트 평균 0.3 → needs_review.
2. 경계값: 박스 정확히 0.7 + 평균 정확히 0.5 → auto_accepted(≥ 통일).
3. 키포인트 평균 계산이 인터랙터의 순수 함수로 검증 가능한지(스텁 데이터로 산술 고정).

## 7. RTX 3050 체크리스트 / 수용 기준

- [ ] 신규 의존성 0개, 모델 1회 로드.
- [ ] 좌표 단위가 계약에 명시(픽셀)되고 정규화 좌표 혼입 없음.
- [ ] 게이팅(2중 조건 포함) 결정적 코드 + 스텁 테스트 통과 + `lint-imports` KEPT.
- [ ] 파인튜닝 시 ultralytics pose yaml 경로 — 별도 학습 슬라이스 신설 금지(기존 face_training 패턴 참고).
