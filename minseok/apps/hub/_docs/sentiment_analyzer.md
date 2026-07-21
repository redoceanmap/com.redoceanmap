# 감정 분석 (Sentiment Analysis) — 구현 지시서 (허브 언어 슬라이스)

> 원 과제: **Transformer 직접 구현 감정 분석** (IMDb 영화평 수준). 이 문서는 그것을
> RTX 3050(8GB) + 이 프로젝트 구조·**기존 자산**에 맞게 번역한 작업 명세다.
> 하네스 원칙·아키텍처 매핑은 [[minseok/apps/hub/_docs/image_classifier|image_classifier]] §1·§2를 그대로 따른다.

---

## 0. 기존 자산 먼저 확인 (중요 — 중복 구현 금지)

이 프로젝트에는 감정/분류 파이프라인이 이미 두 갈래 있다:

1. **mail watcher** — KcELECTRA로 유해 텍스트 분류 (transformers 추론 패턴 보유, `ModerationPort`).
2. **news_labels** — EXAONE 7.8B 배치 라벨링(`scripts/label_news.py`), `(news_id, labeler)` 유니크로
   **라벨러 버전이 공존**하는 구조.

따라서 이 슬라이스의 목적은 "감정 분석 신규 발명"이 아니라 **경량 전용 분류기를 세 번째
라벨러로 추가**하고, 범용 텍스트 감성 도구를 HTTP로 노출하는 것이다.

## 1. 대체 모델 추천

| | 원 과제 | 추천 | 근거 |
|---|---|---|---|
| 모델 | Transformer 밑바닥 구현 | **KcELECTRA-base 파인튜닝** (beomi/KcELECTRA-base-v2022, 110M) | 한국어 구어·뉴스에 강한 사전학습. 110M은 8GB에서 **full FT 가능 — LoRA조차 불필요**. transformers 이미 보유, mail watcher와 동일 스택 |
| 파인튜닝 | 밑바닥 학습 | HF `Trainer`, fp16, batch 32, max_len 256 → ~4GB | 금융 감성 데이터(KLUE·자체 news_labels 증류)로 3~5 epoch |
| 대안 (QLoRA) | — | EXAONE 7.8B + QLoRA(4bit, r=16) | 8GB에서 batch 1·seq 512·grad ckpt로 **가능은 하나 빠듯**. 분류 태스크에 7.8B는 과체급 — 추론 비용도 상시 서빙에 부적합. 라벨 품질 상한이 필요할 때만 선택 |

**결론**: 기본은 KcELECTRA full FT. QLoRA는 이 과제에선 선택지로만 남긴다
(QLoRA가 정말 필요한 체급은 [[minseok/apps/hub/_docs/video_classifier|video_classifier]] 참고).

## 2. 슬라이스 파일 (1:1 — `apps/hub/` 기준, prefix는 /language — 비전 아님)

```
adapter/inbound/api/schemas/sentiment_analyzer_schema.py
adapter/inbound/api/v1/sentiment_analyzer_router.py       # POST /language/sentiments
app/dtos/sentiment_analyzer_dto.py
app/ports/input/sentiment_analyzer_use_case.py
app/ports/output/sentiment_analyzer_port.py
app/use_cases/sentiment_analyzer_interactor.py
adapter/outbound/resource_adapters/electra/kcelectra_sentiment_adapter.py
dependencies/sentiment_analyzer_provider.py               # @lru_cache 싱글턴
scripts/finetune_sentiment.py                             # 학습 스크립트 (서버 코드와 분리)
tests/app/use_cases/test_sentiment_analyzer_interactor.py
```

새 prefix `/language/*`는 hub CLAUDE 라우터 표에 행으로 추가한다.

## 3. 포트 계약

```python
class SentimentAnalyzerPort(ABC):
    @abstractmethod
    def analyze(self, text: str) -> list[tuple[str, float]]:
        """(라벨, softmax 확률)을 확률 내림차순으로 반환한다. 라벨 셋: positive/negative/neutral
        (모델 config의 id2label에서 유도 — 하드코딩 금지)."""
```

## 4. 게이팅 (인터랙터 — 결정적, image_classifier와 동일 3분기)

```
top-1 ≥ SENTIMENT_HIGH (0.8)   → auto_accepted
≥ SENTIMENT_LOW (0.5)          → needs_review
미만                            → human_required
```

- 입력 검증(라우터): 빈 문자열 400, `SENTIMENT_MAX_CHARS`(2000) 초과 400.
- 로그 1줄: `감정 분석: chars=%d, latency_ms=%d, top1=%.4f, label=%s, decision=%s`
  — **원문 텍스트는 로깅 금지**(개인정보), 길이만.

## 5. news_labels 라벨러로 편입 (선택 2단계)

파인튜닝 모델이 검증되면 `scripts/label_news.py`에 라벨러로 추가한다:

- labeler 값: `"kcelectra-sentiment-v1"` — 기존 EXAONE 라벨과 **같은 뉴스에 공존**
  ((news_id, labeler) 유니크가 이미 이를 허용).
- 정답은 실현 수익률(price_bars 조인)이므로, 두 라벨러의 품질 비교가 데이터로 가능해진다.
- 이 단계는 별도 커밋 — HTTP 슬라이스 완성과 섞지 않는다.

## 6. 설정 (`core/config.py`)

```python
SENTIMENT_MODEL_PATH = os.getenv("SENTIMENT_MODEL_PATH", "")   # 파인튜닝 산출 경로. 비면 503 (열화)
SENTIMENT_HIGH = float(os.getenv("SENTIMENT_HIGH", "0.8"))
SENTIMENT_LOW = float(os.getenv("SENTIMENT_LOW", "0.5"))
SENTIMENT_MAX_CHARS = int(os.getenv("SENTIMENT_MAX_CHARS", "2000"))
```

## 7. 파인튜닝 레시피 (RTX 3050 8GB)

`scripts/finetune_sentiment.py` (독립 스크립트):

```
base=beomi/KcELECTRA-base-v2022, fp16, per_device_train_batch_size=32,
max_length=256, lr=2e-5, epochs=3, eval 지표=macro-F1
```

- 데이터: 공개 한국어 감성 셋 + (선택) 기존 EXAONE news_labels를 약지도 라벨로 증류.
- 산출물을 `SENTIMENT_MODEL_PATH`로 지정 — 서버 코드 변경 없이 반영.

## 8. 테스트 / 수용 기준

- [ ] 스텁 포트로 3분기 + 경계값(정확히 0.8/0.5) 테스트 통과 — 모델 로딩 없음.
- [ ] 라벨 셋이 모델 메타(id2label)에서 유도, 하드코딩 0개.
- [ ] 원문 텍스트가 로그에 남지 않는다.
- [ ] 모델 경로 미설정 시 앱 기동은 정상, 해당 엔드포인트만 503.
- [ ] mail watcher의 기존 ModerationPort는 변경하지 않는다. `lint-imports` KEPT.
