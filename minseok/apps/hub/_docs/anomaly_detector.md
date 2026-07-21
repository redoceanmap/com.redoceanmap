# 이상 화상 탐지 (Visual Anomaly Detection) — 구현 지시서 (허브 비전 슬라이스)

> 원 과제: **AnoGAN · Efficient GAN** (~2017-18, GAN 재구성 오차 방식). 이 문서는 그것을
> RTX 3050(8GB) + 이 프로젝트 구조에 맞는 현대 대체 모델로 번역한 작업 명세다.
> 하네스 원칙·아키텍처 매핑은 [[minseok/apps/hub/_docs/image_classifier|image_classifier]] §1·§2를 그대로 따른다.

---

## 0. 대체 모델 추천 — GAN 재구성 방식은 폐기한다

| | 원 모델 | 추천 | 근거 |
|---|---|---|---|
| 모델 | AnoGAN / Efficient GAN | **PatchCore** (anomalib) | GAN 역사상(잠재 벡터 역탐색·재구성 오차) 방식은 느리고 불안정. PatchCore는 사전학습 백본 특징의 메모리 뱅크 방식 — **역전파 학습 자체가 거의 없고** 정상 샘플 수십~수백 장이면 MVTec 기준 GAN 계열을 압도 |
| 학습 | GAN 이중 네트워크 적대 학습 | 정상 이미지 특징 수집 1회 (분 단위, 8GB 여유) | 재학습 = 메모리 뱅크 재구축. 모델 드리프트 관리가 단순 |
| 대안 | — | EfficientAD (동일 anomalib) | ms 단위 추론이 필요할 때(실시간 라인 검사). 배치성 검사면 PatchCore 기본 |

**신규 의존성**: `anomalib` (lightning 포함 — 무겁다. 학습·뱅크 구축은 스크립트로 분리하고,
서빙은 anomalib 추론 API만 사용).

## 1. 학습(뱅크 구축)과 서빙의 분리

- **구축**: `scripts/build_anomaly_bank.py` (독립 스크립트 — market 3NF 적재 스크립트와 같은 위상).
  정상 이미지 디렉토리를 입력받아 PatchCore 메모리 뱅크를 만들고 `ANOMALY_MODEL_PATH`에 저장.
  임계값은 검증 세트에서 F1 최적점을 계산해 **숫자로 함께 저장**한다(런타임 재추정 금지 — 결정적).
- **서빙**: 어댑터는 저장된 뱅크를 로드해 추론만 한다. 뱅크 파일이 없으면 계약 예외
  `AnomalyModelUnavailable` → 라우터 503 (열화 동작 명시).

## 2. 슬라이스 파일 (1:1 — `apps/hub/` 기준)

```
adapter/inbound/api/schemas/anomaly_detector_schema.py
adapter/inbound/api/v1/anomaly_detector_router.py         # POST /vision/anomalies
app/dtos/anomaly_detector_dto.py
app/ports/input/anomaly_detector_use_case.py
app/ports/output/anomaly_detector_port.py                 # + AnomalyModelUnavailable
app/use_cases/anomaly_detector_interactor.py
adapter/outbound/resource_adapters/anomalib/patchcore_adapter.py
dependencies/anomaly_detector_provider.py                 # @lru_cache 싱글턴
scripts/build_anomaly_bank.py                             # 정상 샘플 → 메모리 뱅크 + 임계값
tests/app/use_cases/test_anomaly_detector_interactor.py
```

## 3. 포트 계약

```python
class AnomalyDetectorPort(ABC):
    @abstractmethod
    def score(self, image: bytes) -> float:
        """이상 점수(0~1 정규화)를 반환한다. 높을수록 이상. 디코딩 불가는 UnreadableImageError,
        뱅크 미구축은 AnomalyModelUnavailable."""

    @abstractmethod
    def threshold(self) -> float:
        """뱅크 구축 시 저장된 판정 임계값(F1 최적점)을 반환한다."""
```

점수 정규화(min-max 캘리브레이션 값)도 뱅크 구축 시 저장 — 런타임에 어떤 통계도 재추정하지 않는다.

## 4. 게이팅 (인터랙터 — 결정적)

이상 탐지는 오탐 비용과 미탐 비용이 비대칭이다. 임계값 1개가 아니라 **밴드**로 판정한다:

```
score < threshold × ANOMALY_CLEAR_RATIO (0.8)   → decision = "normal"        (여유 있는 정상)
threshold × 0.8 ≤ score < threshold             → decision = "needs_review"  (경계 — 사람 확인 권장)
score ≥ threshold                                → decision = "anomaly"       (이상 확정)
```

로그 1줄: `이상 탐지: file=%s, latency_ms=%d, score=%.4f, threshold=%.4f, decision=%s`.

## 5. 설정 (`core/config.py`)

```python
ANOMALY_MODEL_PATH = os.getenv("ANOMALY_MODEL_PATH", "")     # 비면 슬라이스 503 (열화 동작)
ANOMALY_CLEAR_RATIO = float(os.getenv("ANOMALY_CLEAR_RATIO", "0.8"))
```

## 6. 테스트 (모델 없이 스텁 포트)

1. 3분기: threshold=0.5 스텁에서 score 0.3 → normal / 0.45 → needs_review / 0.6 → anomaly.
2. 경계값: score가 정확히 threshold → anomaly, 정확히 threshold×0.8 → needs_review(≥ 통일).
3. 뱅크 미구축 스텁(`AnomalyModelUnavailable`) → 인터랙터가 삼키지 않고 그대로 전파.

## 7. RTX 3050 체크리스트 / 수용 기준

- [ ] 뱅크 구축은 스크립트, 서빙은 로드만 — 서버 프로세스에서 학습 코드가 돌지 않는다.
- [ ] 임계값·정규화 통계가 뱅크와 함께 저장되고 런타임 재추정이 없다.
- [ ] 판정 밴드(정상/경계/이상)가 결정적 코드 + 스텁 테스트로 고정된다.
- [ ] anomalib 미설치 환경(맥 등)에서도 앱 기동이 죽지 않는다(어댑터 지연 import + 503).
- [ ] `lint-imports` KEPT.
