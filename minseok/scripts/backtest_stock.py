"""주식 방향 전망 백테스트 — OutlookPredictor의 지표 신호 적중률 채점.

과거 뉴스는 수집할 수 없으므로 감성은 중립(0.0) 고정, 지표(RSI·MA 추세) 신호만
평가한다. 항상-UP 기준선과 비교해 신호가 순진한 전략보다 나은지 본다.

--regime: SPY 200일선·VIX로 레짐 달력을 만들어 분포를 국면별로도 분할(표본 실측용).
--earnings-veto: yfinance 발표일(~12분기)로 어닝 ±2일 평가일을 제외.

사용:
  venv/bin/python minseok/scripts/backtest_stock.py 005930 AAPL --period 2y --horizon 5
  venv/bin/python minseok/scripts/backtest_stock.py AAPL --period 10y --regime --earnings-veto
"""

import argparse
import sys
from datetime import UTC, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # minseok
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "apps"))

import yfinance as yf  # noqa: E402

from stock.adapter.outbound.yfinance_market_data_adapter import yahoo_candidates  # noqa: E402
from stock.domain.entities.price_bar import PriceBar  # noqa: E402
from stock.domain.services.backtester import Backtester  # noqa: E402
from stock.domain.services.regime_calendar import RegimeCalendar  # noqa: E402


def fetch_history(code: str, period: str):
    for ticker in yahoo_candidates(code):
        history = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        if not history.empty:
            return ticker, history
    raise SystemExit(f"시세 데이터를 찾지 못했습니다: {code}")


def _bars(ticker: str, history) -> list[PriceBar]:
    idx = history.index.tz_convert(UTC) if history.index.tz is not None else history.index.tz_localize(UTC)
    return [
        PriceBar(
            ticker=ticker, timeframe="1d", ts=ts.to_pydatetime(),
            open=float(r["Open"]), high=float(r["High"]), low=float(r["Low"]),
            close=float(r["Close"]), volume=0,
        )
        for ts, (_, r) in zip(idx, history.iterrows())
    ]


def build_calendar() -> RegimeCalendar:
    spy = _bars("SPY", fetch_history("SPY", "max")[1])
    vix = _bars("^VIX", fetch_history("^VIX", "max")[1])
    return RegimeCalendar.from_bars(spy, vix)


def earnings_veto_dates(ticker: str) -> set:
    try:
        df = yf.Ticker(ticker).get_earnings_dates(limit=20)
    except Exception as e:
        print(f"  [경고] {ticker} 발표일 조회 실패({e}) — veto 없이 진행")
        return set()
    if df is None or df.empty:
        return set()
    return {
        d + timedelta(days=off)
        for d in {ts.date() for ts in df.index}
        for off in range(-2, 3)
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="방향 전망 백테스트")
    parser.add_argument("symbols", nargs="+", help="종목 코드 (예: 005930 AAPL)")
    parser.add_argument("--period", default="2y", help="이력 기간 (yfinance 형식, 기본 2y)")
    parser.add_argument("--horizon", type=int, default=5, help="평가 구간 거래일 (기본 5)")
    parser.add_argument("--regime", action="store_true", help="SPY·VIX 레짐 조건화 분포 출력")
    parser.add_argument("--earnings-veto", action="store_true", help="어닝 ±2일 평가일 제외")
    args = parser.parse_args()

    backtester = Backtester()
    calendar = build_calendar() if args.regime else None
    for code in args.symbols:
        ticker, history = fetch_history(code, args.period)
        closes = [float(v) for v in history["Close"]]
        lows = [float(v) for v in history["Low"]]
        highs = [float(v) for v in history["High"]]

        report = backtester.run(closes=closes, lows=lows, highs=highs, horizon=args.horizon)
        hit = f"{report.hit_rate:.1%}" if report.hit_rate is not None else "N/A(신호 없음)"
        print(
            f"[{code} → {ticker}] 평가 {report.evaluated}일 · {report.horizon_days}일 전망\n"
            f"  신호: UP {report.up_signals} / DOWN {report.down_signals} / 중립 {report.neutral_signals}\n"
            f"  적중률: {hit} (적중 {report.hits}/{report.actionable})\n"
            f"  기준선(항상 UP): {report.baseline_up_rate:.1%}\n"
        )

        if not (args.regime or args.earnings_veto):
            continue
        bars = _bars(ticker, history)
        regimes = [calendar.regime_at(b.ts.date()) for b in bars] if calendar else None
        veto = earnings_veto_dates(ticker) if args.earnings_veto else set()
        excluded = [b.ts.date() in veto for b in bars] if veto else None
        dist = backtester.distribution(
            closes, lows, highs, horizon=args.horizon, regimes=regimes, excluded=excluded,
        )
        if dist.vetoed:
            print(f"  어닝 veto 제외: {dist.vetoed}일 (평가 {dist.evaluated}일로 축소)")
        for regime, stats in sorted(dist.by_regime.items()):
            print(f"  [{regime}] 평가 {stats.evaluated}일 · 기준선 {stats.baseline_up_rate:.1%}")
            for direction in ("UP", "DOWN", "NEUTRAL"):
                d = stats.by_direction[direction]
                if d.sample_size == 0:
                    continue
                print(f"    {direction}: n={d.sample_size} 상승 {d.hits / d.sample_size:.1%}")
        print()


if __name__ == "__main__":
    main()
