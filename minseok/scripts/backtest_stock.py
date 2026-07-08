"""주식 방향 전망 백테스트 — OutlookPredictor의 지표 신호 적중률 채점.

과거 뉴스는 수집할 수 없으므로 감성은 중립(0.0) 고정, 지표(RSI·MA 추세) 신호만
평가한다. 항상-UP 기준선과 비교해 신호가 순진한 전략보다 나은지 본다.

사용:
  venv/bin/python minseok/scripts/backtest_stock.py 005930 AAPL --period 2y --horizon 5
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # minseok
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "apps"))

import yfinance as yf  # noqa: E402

from stock.adapter.outbound.yfinance_market_data_adapter import yahoo_candidates  # noqa: E402
from stock.domain.services.backtester import Backtester  # noqa: E402


def fetch_history(code: str, period: str):
    for ticker in yahoo_candidates(code):
        history = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        if not history.empty:
            return ticker, history
    raise SystemExit(f"시세 데이터를 찾지 못했습니다: {code}")


def main() -> None:
    parser = argparse.ArgumentParser(description="방향 전망 백테스트")
    parser.add_argument("symbols", nargs="+", help="종목 코드 (예: 005930 AAPL)")
    parser.add_argument("--period", default="2y", help="이력 기간 (yfinance 형식, 기본 2y)")
    parser.add_argument("--horizon", type=int, default=5, help="평가 구간 거래일 (기본 5)")
    args = parser.parse_args()

    backtester = Backtester()
    for code in args.symbols:
        ticker, history = fetch_history(code, args.period)
        report = backtester.run(
            closes=[float(v) for v in history["Close"]],
            lows=[float(v) for v in history["Low"]],
            highs=[float(v) for v in history["High"]],
            horizon=args.horizon,
        )
        hit = f"{report.hit_rate:.1%}" if report.hit_rate is not None else "N/A(신호 없음)"
        print(
            f"[{code} → {ticker}] 평가 {report.evaluated}일 · {report.horizon_days}일 전망\n"
            f"  신호: UP {report.up_signals} / DOWN {report.down_signals} / 중립 {report.neutral_signals}\n"
            f"  적중률: {hit} (적중 {report.hits}/{report.actionable})\n"
            f"  기준선(항상 UP): {report.baseline_up_rate:.1%}\n"
        )


if __name__ == "__main__":
    main()
