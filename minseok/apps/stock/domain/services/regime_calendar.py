from __future__ import annotations

from bisect import bisect_right
from datetime import date

from stock.domain.entities.price_bar import PriceBar

REGIME_BULL = "BULL"          # SPY 종가 > 200일선
REGIME_BEAR = "BEAR"          # SPY 종가 ≤ 200일선
REGIME_HIGH_VOL = "HIGH_VOL"  # VIX 종가 > 임계 — 강세/약세보다 우선(공포 국면은 별도 취급)

SPY_MA_PERIOD = 200   # 레짐 전용 — IndicatorCalculator의 MA_LONG(50)과 무관(최소 봉 제약 불변)
VIX_HIGH = 25.0


class RegimeCalendar:
    """시장 레짐 달력 — 지수 일봉(SPY·VIX)으로 날짜→레짐을 판정하는 순수 도메인 서비스.

    비거래일·휴장 갭은 직전 거래일 값으로 forward-fill(bisect). 지수 데이터가 없거나
    해당 날짜에 SPY 200일선이 아직 안 만들어졌으면 None(무레짐) — 호출부는 무조건부
    통계로 폴백한다. 한국 종목에도 SPY/VIX 레짐을 그대로 적용한다(단순화 —
    워치리스트 대부분이 미국이고, 한국 대형주도 미국 국면과 동조성이 높다).
    """

    def __init__(
        self,
        spy_dates: list[date],
        spy_regimes: list[str],
        vix_dates: list[date],
        vix_closes: list[float],
    ) -> None:
        self._spy_dates = spy_dates      # 오름차순 — MA200 형성 이후 구간만
        self._spy_regimes = spy_regimes  # spy_dates와 정렬(BULL/BEAR)
        self._vix_dates = vix_dates      # 오름차순
        self._vix_closes = vix_closes

    @classmethod
    def from_bars(cls, spy_bars: list[PriceBar], vix_bars: list[PriceBar]) -> "RegimeCalendar":
        """지수 일봉(ts 오름차순) → 달력. 빈 입력이어도 생성된다(전 날짜 None)."""
        spy_dates: list[date] = []
        spy_regimes: list[str] = []
        closes = [b.close for b in spy_bars]
        for i, bar in enumerate(spy_bars):
            if i + 1 < SPY_MA_PERIOD:
                continue  # 200일선 미형성 구간 — 판정 불가
            ma = sum(closes[i + 1 - SPY_MA_PERIOD: i + 1]) / SPY_MA_PERIOD
            spy_dates.append(bar.ts.date())
            spy_regimes.append(REGIME_BULL if bar.close > ma else REGIME_BEAR)
        return cls(
            spy_dates=spy_dates,
            spy_regimes=spy_regimes,
            vix_dates=[b.ts.date() for b in vix_bars],
            vix_closes=[b.close for b in vix_bars],
        )

    def regime_at(self, d: date) -> str | None:
        """날짜 d의 레짐 — 직전 거래일 forward-fill. 판정 재료가 없으면 None."""
        spy_idx = bisect_right(self._spy_dates, d) - 1
        if spy_idx < 0:
            return None
        vix_idx = bisect_right(self._vix_dates, d) - 1
        if vix_idx >= 0 and self._vix_closes[vix_idx] > VIX_HIGH:
            return REGIME_HIGH_VOL
        return self._spy_regimes[spy_idx]
