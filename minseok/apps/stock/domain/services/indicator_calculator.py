from __future__ import annotations

from stock.domain.value_objects.indicators import Indicators

RSI_PERIOD = 14
MA_SHORT = 20
MA_LONG = 50
SUPPORT_RESISTANCE_WINDOW = 60  # 최근 N거래일 저점/고점을 지지/저항으로 본다
ATR_PERIOD = 14
BB_PERIOD = 20
BB_STDDEV = 2.0
VOLUME_SHORT = 5
VOLUME_LONG = 20
OBV_WINDOW = 20


class IndicatorCalculator:
    """일봉 시계열(종가·저가·고가·거래량) → 기술적 지표. 외부 의존 없는 순수 도메인 서비스.

    CPU-bound 순수 계산이므로 동기(def)로 둔다. RSI는 Wilder 평활 방식.
    지지/저항은 최근 윈도 저점/고점 휴리스틱 — 정밀화(피벗 등)는 백테스트로 검증 후.
    volumes가 없으면 거래량 파생 지표(volume_ratio·obv_slope)는 중립값으로 둔다.
    """

    def compute(
        self,
        closes: list[float],
        lows: list[float],
        highs: list[float],
        volumes: list[float] | None = None,
    ) -> Indicators:
        if len(closes) < MA_LONG + 1:
            raise ValueError(f"지표 계산에는 최소 {MA_LONG + 1}개 종가가 필요합니다 (현재 {len(closes)}개).")
        volume_ratio, obv_slope = 1.0, 0.0
        if volumes is not None and len(volumes) >= VOLUME_LONG + 1:
            volume_ratio = self._volume_ratio(volumes)
            obv_slope = self._obv_slope(closes, volumes)
        return Indicators(
            rsi=self._rsi(closes, RSI_PERIOD),
            ma20=self._sma(closes, MA_SHORT),
            ma50=self._sma(closes, MA_LONG),
            support=min(lows[-SUPPORT_RESISTANCE_WINDOW:]),
            resistance=max(highs[-SUPPORT_RESISTANCE_WINDOW:]),
            atr_pct=self._atr_pct(closes, lows, highs, ATR_PERIOD),
            bb_percent_b=self._bb_percent_b(closes, BB_PERIOD, BB_STDDEV),
            volume_ratio=volume_ratio,
            obv_slope=obv_slope,
        )

    @staticmethod
    def _sma(values: list[float], period: int) -> float:
        return sum(values[-period:]) / period

    @staticmethod
    def _rsi(closes: list[float], period: int) -> float:
        deltas = [closes[i + 1] - closes[i] for i in range(len(closes) - 1)]
        gains = [max(d, 0.0) for d in deltas]
        losses = [max(-d, 0.0) for d in deltas]

        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        for gain, loss in zip(gains[period:], losses[period:]):
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period

        if avg_loss == 0.0:
            return 100.0 if avg_gain > 0.0 else 50.0
        rs = avg_gain / avg_loss
        return 100.0 - 100.0 / (1.0 + rs)

    @staticmethod
    def _atr_pct(closes: list[float], lows: list[float], highs: list[float], period: int) -> float:
        # True Range = max(고-저, |고-전일종가|, |저-전일종가|). ATR은 최근 period 단순 평균 근사
        true_ranges = [
            max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
            for i in range(len(closes) - period, len(closes))
        ]
        atr = sum(true_ranges) / period
        last_close = closes[-1]
        return atr / last_close if last_close > 0 else 0.0

    @staticmethod
    def _bb_percent_b(closes: list[float], period: int, stddev: float) -> float:
        window = closes[-period:]
        mid = sum(window) / period
        variance = sum((v - mid) ** 2 for v in window) / period
        sd = variance ** 0.5
        if sd == 0.0:
            return 0.5
        lower = mid - stddev * sd
        upper = mid + stddev * sd
        return (closes[-1] - lower) / (upper - lower)

    @staticmethod
    def _volume_ratio(volumes: list[float]) -> float:
        long_avg = sum(volumes[-VOLUME_LONG:]) / VOLUME_LONG
        if long_avg <= 0:
            return 1.0
        short_avg = sum(volumes[-VOLUME_SHORT:]) / VOLUME_SHORT
        return short_avg / long_avg

    @staticmethod
    def _obv_slope(closes: list[float], volumes: list[float]) -> float:
        # OBV: 상승일 +거래량, 하락일 -거래량 누적. 최근 윈도 순증분을 (평균 거래량×윈도)로 정규화 → 대체로 -1~1
        obv_delta = 0.0
        for i in range(len(closes) - OBV_WINDOW, len(closes)):
            if closes[i] > closes[i - 1]:
                obv_delta += volumes[i]
            elif closes[i] < closes[i - 1]:
                obv_delta -= volumes[i]
        avg_volume = sum(volumes[-OBV_WINDOW:]) / OBV_WINDOW
        return obv_delta / (avg_volume * OBV_WINDOW) if avg_volume > 0 else 0.0
