"""피처 조합 스윕 백테스트 — 로드맵 ①-M2 재채점.

거래량(OBV)·변동성(ATR·볼린저 %B) 피처를 추가한 뒤, 조합별로 다종목 집계 성적을
채점한다. "확률 제시 가능" 판정 기준(도메인 backtest_report에 명문화):
방향별 신호 표본 n≥100 + Wilson 95% 신뢰구간 하한이 기준선(항상-UP/-DOWN)을 초과.

사용:
  venv/bin/python minseok/scripts/backtest_sweep.py --period 5y --horizon 5
"""

import argparse
import sys
from functools import reduce
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # minseok
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "apps"))

import yfinance as yf  # noqa: E402

from stock.adapter.outbound.yfinance_market_data_adapter import yahoo_candidates  # noqa: E402
from stock.domain.entities.analysis_config import AnalysisConfig  # noqa: E402
from stock.domain.services.backtester import Backtester  # noqa: E402
from stock.domain.value_objects.backtest_report import (  # noqa: E402
    BacktestReport,
    wilson_lower_bound,
)

KR_TICKERS = [
    "005930", "000660", "005380", "051910", "035420", "035720",
    "068270", "000270", "005490", "105560", "006400", "373220",
]
US_TICKERS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META",
    "TSLA", "AVGO", "TSM", "ORCL", "AMD", "INTC",
]

# 조합 × 임계값 스윕. 감성은 백테스트에서 항상 중립(0)이라 w_sentiment는 무의미.
_FEATURE_SETS: dict[str, dict] = {
    "RSI+MA(기존)": dict(w_rsi=0.5, w_trend=0.5, w_bb=0.0, w_obv=0.0),
    "BB단독": dict(w_rsi=0.0, w_trend=0.0, w_bb=1.0, w_obv=0.0),
    "OBV단독": dict(w_rsi=0.0, w_trend=0.0, w_bb=0.0, w_obv=1.0),
    "RSI+BB": dict(w_rsi=0.5, w_trend=0.0, w_bb=0.5, w_obv=0.0),
    "추세+OBV": dict(w_rsi=0.0, w_trend=0.5, w_bb=0.0, w_obv=0.5),
    "전체결합": dict(w_rsi=0.3, w_trend=0.2, w_bb=0.3, w_obv=0.2),
    "전체+ATR거부(4%)": dict(w_rsi=0.3, w_trend=0.2, w_bb=0.3, w_obv=0.2, atr_veto=0.04),
}
_THRESHOLDS = [0.15, 0.25, 0.35]


def build_configs() -> list[tuple[str, AnalysisConfig]]:
    combos = []
    for name, weights in _FEATURE_SETS.items():
        for th in _THRESHOLDS:
            combos.append((
                f"{name} ±{th}",
                AnalysisConfig(up_threshold=th, down_threshold=-th, w_sentiment=0.0, **weights),
            ))
    return combos


def fetch(code: str, period: str):
    for ticker in yahoo_candidates(code):
        history = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        if not history.empty:
            return ticker, history
    return None, None


def main() -> None:
    parser = argparse.ArgumentParser(description="피처 조합 스윕 백테스트")
    parser.add_argument("--period", default="5y")
    parser.add_argument("--horizon", type=int, default=5)
    args = parser.parse_args()

    combos = build_configs()
    backtester = Backtester()
    merged: list[BacktestReport | None] = [None] * len(combos)
    fetched = 0

    for code in KR_TICKERS + US_TICKERS:
        ticker, history = fetch(code, args.period)
        if history is None:
            print(f"[skip] {code}: 시세 없음", file=sys.stderr)
            continue
        fetched += 1
        reports = backtester.sweep(
            closes=[float(v) for v in history["Close"]],
            lows=[float(v) for v in history["Low"]],
            highs=[float(v) for v in history["High"]],
            volumes=[float(v) for v in history["Volume"]],
            horizon=args.horizon,
            configs=[c for _, c in combos],
        )
        merged = [r if m is None else m.merged(r) for m, r in zip(merged, reports)]
        print(f"[{code} → {ticker}] {reports[0].evaluated}일 평가 완료", file=sys.stderr)

    print(f"\n종목 {fetched}개 · {args.period} · horizon {args.horizon}일 — 집계 성적표\n")
    header = (
        f"{'조합':<28} {'UP n':>6} {'UP적중':>7} {'UP하한':>7} {'기준선':>7} {'판정':>4}"
        f" | {'DN n':>6} {'DN적중':>7} {'DN하한':>7} {'역기준':>7} {'판정':>4}"
    )
    print(header)
    print("-" * len(header))
    for (name, _), report in zip(combos, merged):
        if report is None:
            continue
        up_rate = f"{report.up_hit_rate:.1%}" if report.up_hit_rate is not None else "-"
        dn_rate = f"{report.down_hit_rate:.1%}" if report.down_hit_rate is not None else "-"
        up_low = f"{wilson_lower_bound(report.up_hits, report.up_signals):.1%}" if report.up_signals else "-"
        dn_low = f"{wilson_lower_bound(report.down_hits, report.down_signals):.1%}" if report.down_signals else "-"
        print(
            f"{name:<28} {report.up_signals:>6} {up_rate:>7} {up_low:>7}"
            f" {report.baseline_up_rate:>6.1%} {'✅' if report.up_probability_ready else '❌':>4}"
            f" | {report.down_signals:>6} {dn_rate:>7} {dn_low:>7}"
            f" {1 - report.baseline_up_rate:>6.1%} {'✅' if report.down_probability_ready else '❌':>4}"
        )


if __name__ == "__main__":
    main()
