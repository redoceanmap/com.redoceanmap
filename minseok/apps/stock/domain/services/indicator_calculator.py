from __future__ import annotations

from stock.domain.value_objects.indicators import Indicators

RSI_PERIOD = 14
MA_SHORT = 20
MA_LONG = 50
SUPPORT_RESISTANCE_WINDOW = 60  # 최근 N거래일 저점/고점을 지지/저항으로 본다


class IndicatorCalculator:
    """일봉 시계열(종가·저가·고가) → 기술적 지표. 외부 의존 없는 순수 도메인 서비스.

    CPU-bound 순수 계산이므로 동기(def)로 둔다. RSI는 Wilder 평활 방식.
    지지/저항은 최근 윈도 저점/고점 휴리스틱 — 정밀화(피벗 등)는 백테스트로 검증 후.
    """

    def compute(self, closes: list[float], lows: list[float], highs: list[float]) -> Indicators:
        if len(closes) < MA_LONG + 1:
            raise ValueError(f"지표 계산에는 최소 {MA_LONG + 1}개 종가가 필요합니다 (현재 {len(closes)}개).")
        return Indicators(
            rsi=self._rsi(closes, RSI_PERIOD),
            ma20=self._sma(closes, MA_SHORT),
            ma50=self._sma(closes, MA_LONG),
            support=min(lows[-SUPPORT_RESISTANCE_WINDOW:]),
            resistance=max(highs[-SUPPORT_RESISTANCE_WINDOW:]),
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
