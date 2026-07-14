"""뉴스 LLM 라벨링 — EXAONE 2.4B AWQ(로컬)로 감성·이벤트·확신도 라벨 → 허브 적재.

허브에서 미라벨 뉴스를 받아(/automation/news-labels/pending) 라벨 후 되돌린다
(/automation/news-labels). 라벨은 학습 피처 — 정답은 실현 수익률(price_bars 조인)이 담당한다.

모델 계층 바인딩: 라벨링은 도메인 내부 추론이므로 2.4B를 쓴다(minseok CLAUDE).
앱 런타임과 달리 cron 스크립트라 오케스트레이터(Ollama)가 아닌 루트 .venv HF 직로딩을 쓴다 —
결과는 허브 HTTP 계약으로만 적재한다(collect_news/collect_prices 발자국).

실행 (루트 .venv — torch/transformers 필요, minseok/venv 아님):
    ../.venv/bin/python scripts/label_news.py              # 미라벨 전부(기본 상한 3000)
    ../.venv/bin/python scripts/label_news.py --limit 20   # 상한 지정
    ../.venv/bin/python scripts/label_news.py --dry-run    # 라벨 출력만, 허브 POST 안 함

백엔드 PC cron 예시(매일 02:30 — GPU 유휴 시간대):
    30 2 * * * cd /path/to/minseok && ../.venv/bin/python scripts/label_news.py >> ~/label_news.log 2>&1
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]  # minseok
load_dotenv(ROOT.parent / ".env")

HUB_URL = os.getenv("HUB_URL", "http://localhost:8000")
TOKEN = os.getenv("N8N_INBOUND_TOKEN", "")
HEADERS = {"X-Webhook-Token": TOKEN}

MODEL_DIR = ROOT.parent / "EXAONE-3.5-2.4B-Instruct-AWQ"
LABELER = "exaone-2.4b-awq"
EVENT_TYPES = ("실적", "목표가·투자의견", "신제품·기술", "규제·소송", "거시", "수급·지분", "기타")
POST_CHUNK = 200

SYSTEM = "너는 금융 뉴스 라벨러다. 반드시 JSON 한 줄로만 답한다. 설명을 덧붙이지 않는다."
PROMPT = """다음 뉴스 제목이 종목 {ticker}의 주가에 호재인지 악재인지 라벨링하라.

규칙:
- sentiment: 주가가 오를 뉴스면 양수(+), 내릴 뉴스면 음수(-), 영향 없으면 0.0. 범위 -1.0 ~ 1.0.
  주의: 부정적 단어(절벽·부족·제약)가 있어도 그것이 이 종목에 유리하면(예: 공급 부족 → 가격 상승 수혜) 호재다.
- event: 실적(실적 발표·전망) | 목표가·투자의견(증권사 등급·목표가) | 신제품·기술(제품·수주·증설·기술)
  | 규제·소송(정부 규제·소송·노사 분쟁) | 거시(금리·환율·업황 전반) | 수급·지분(지분 매매·자사주·공매도) | 기타
- confidence: 판단 확신도 0.0 ~ 1.0

예시:
제목: 삼성전자, 4분기 영업이익 시장 기대 상회 → {{"sentiment": 0.7, "event": "실적", "confidence": 0.9}}
제목: 모건스탠리, 애플 목표가 하향…수요 둔화 우려 → {{"sentiment": -0.6, "event": "목표가·투자의견", "confidence": 0.8}}
제목: 엔비디아 주주총회 다음 주 개최 → {{"sentiment": 0.0, "event": "기타", "confidence": 0.6}}

제목: {title} →"""


def fetch_pending(limit: int) -> list[dict]:
    res = requests.get(
        f"{HUB_URL}/automation/news-labels/pending",
        params={"labeler": LABELER, "limit": limit},
        headers=HEADERS, timeout=30,
    )
    res.raise_for_status()
    return res.json()


def post_labels(items: list[dict]) -> int:
    saved = 0
    for start in range(0, len(items), POST_CHUNK):
        res = requests.post(
            f"{HUB_URL}/automation/news-labels",
            json={"items": items[start:start + POST_CHUNK]},
            headers=HEADERS, timeout=60,
        )
        res.raise_for_status()
        saved += res.json()["saved"]
    return saved


def load_model():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, AwqConfig

    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR), trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        str(MODEL_DIR),
        dtype=torch.float16,
        device_map="cuda",
        trust_remote_code=True,
        quantization_config=AwqConfig(bits=4, backend="gemm_triton"),  # Marlin은 nvcc 없어 JIT 실패
    )
    return tokenizer, model


def parse_label(text: str) -> dict | None:
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if not match:
        return None
    try:
        raw = json.loads(match.group())
        return {
            "sentiment": round(max(-1.0, min(1.0, float(raw["sentiment"]))), 2),
            "event": raw["event"] if raw.get("event") in EVENT_TYPES else "기타",
            "confidence": round(max(0.0, min(1.0, float(raw["confidence"]))), 2),
        }
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None


def label_one(tokenizer, model, ticker: str, title: str) -> dict:
    import torch

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": PROMPT.format(
            ticker=ticker, title=title, events=" | ".join(EVENT_TYPES))},
    ]
    inputs = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
    )
    input_ids = inputs["input_ids"] if not isinstance(inputs, torch.Tensor) else inputs
    out = model.generate(
        input_ids.to("cuda"), max_new_tokens=48, do_sample=False,
        pad_token_id=tokenizer.eos_token_id,
    )
    text = tokenizer.decode(out[0][input_ids.shape[1]:], skip_special_tokens=True)
    # 파싱 실패는 중립·확신도 0으로 저장 — 미라벨로 남기면 매 실행 같은 건에서 재실패(수렴 불가)
    return parse_label(text) or {"sentiment": 0.0, "event": "기타", "confidence": 0.0}


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 3000
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] 라벨링 시작 (labeler={LABELER})", flush=True)

    pending = fetch_pending(limit)
    if not pending:
        print("미라벨 뉴스 없음 — 종료", flush=True)
        return
    print(f"미라벨 {len(pending)}건 — 모델 로드 중...", flush=True)
    tokenizer, model = load_model()

    items, parse_failed = [], 0
    for n, news in enumerate(pending, 1):
        label = label_one(tokenizer, model, news["ticker"], news["title"])
        if label["confidence"] == 0.0 and label["event"] == "기타":
            parse_failed += 1
        items.append({
            "newsId": news["newsId"],
            "labeler": LABELER,
            "sentiment": label["sentiment"],
            "eventType": label["event"],
            "confidence": label["confidence"],
        })
        if dry_run and n <= 10:
            print(f"  [{news['ticker']}] {news['title'][:50]} → {label}", flush=True)
        if n % 100 == 0:
            print(f"  진행 {n}/{len(pending)}", flush=True)

    if dry_run:
        print(f"[dry-run] 라벨 {len(items)}건 생성 (파싱 실패 {parse_failed}) — POST 생략", flush=True)
        return
    saved = post_labels(items)
    print(
        f"[{datetime.now():%Y-%m-%d %H:%M:%S}] 합계: 라벨 {len(items)}건 "
        f"(파싱 실패 {parse_failed}) / 신규 저장 {saved}건",
        flush=True,
    )


if __name__ == "__main__":
    main()
