from stock.domain.entities.analysis_config import AnalysisConfig
from stock.domain.entities.outlook import Direction, Outlook
from stock.domain.services.stock_narrator import narrate
from stock.domain.value_objects.indicators import Indicators
from stock.domain.value_objects.signal_breakdown import SignalContribution

_CONFIG = AnalysisConfig.default()


def _ind(**kwargs) -> Indicators:
    base = dict(rsi=50.0, ma20=100.0, ma50=100.0, support=90.0, resistance=110.0)
    base.update(kwargs)
    return Indicators(**base)


def _contrib(sentiment=0.0, rsi=0.0):
    return [
        SignalContribution(key="sentiment", signal=sentiment, weight=0.5, contribution=sentiment * 0.5),
        SignalContribution(key="rsi", signal=rsi, weight=0.3, contribution=rsi * 0.3),
        SignalContribution(key="trend", signal=0.0, weight=0.2, contribution=0.0),
    ]


def _by_key(insights):
    return {i.key: i for i in insights}


def test_UP이면_최대_기여_신호를_지목한다():
    got = _by_key(narrate(
        Outlook(direction=Direction.UP, confidence=0.5),
        0.5, _contrib(sentiment=0.9, rsi=0.2), _ind(), _CONFIG, False,
    ))
    assert "뉴스 감성" in got["summary"].text
    assert got["summary"].tone == "positive"


def test_NEUTRAL_atr_veto_사유_문장():
    got = _by_key(narrate(
        Outlook(direction=Direction.NEUTRAL, confidence=0.0, neutral_reason="atr_veto"),
        0.0, _contrib(), _ind(atr_pct=0.08), _CONFIG, False,
    ))
    assert "변동성" in got["summary"].text
    assert got["summary"].tone == "warning"


def test_NEUTRAL_volume_confirm_사유_문장():
    got = _by_key(narrate(
        Outlook(direction=Direction.NEUTRAL, confidence=0.0, neutral_reason="volume_confirm"),
        0.4, _contrib(), _ind(volume_ratio=0.5), _CONFIG, False,
    ))
    assert "거래량" in got["summary"].text


def test_NEUTRAL_신호_미달_사유_문장():
    got = _by_key(narrate(
        Outlook(direction=Direction.NEUTRAL, confidence=0.1),
        0.1, _contrib(sentiment=0.2), _ind(), _CONFIG, False,
    ))
    assert "기준" in got["summary"].text


def test_RSI_30_경계는_과매도_문장():
    got = _by_key(narrate(
        Outlook(direction=Direction.NEUTRAL, confidence=0.0),
        0.0, _contrib(), _ind(rsi=30.0), _CONFIG, False,
    ))
    assert "과매도" in got["rsi"].text


def test_중립_지표는_문장을_만들지_않는다():
    got = _by_key(narrate(
        Outlook(direction=Direction.NEUTRAL, confidence=0.0),
        0.0, _contrib(), _ind(), _CONFIG, False,
    ))
    # summary만 있고 rsi/trend/bollinger/volume/momentum/volatility는 전부 생략
    assert set(got) == {"summary"}


def test_reference는_True일_때만():
    with_ref = _by_key(narrate(
        Outlook(direction=Direction.NEUTRAL, confidence=0.0),
        0.0, _contrib(), _ind(), _CONFIG, True,
    ))
    without = _by_key(narrate(
        Outlook(direction=Direction.NEUTRAL, confidence=0.0),
        0.0, _contrib(), _ind(), _CONFIG, False,
    ))
    assert "reference" in with_ref
    assert "매수 근거는 아닙니다" in with_ref["reference"].text
    assert "reference" not in without


def test_역배열과_고변동성은_경고_톤():
    got = _by_key(narrate(
        Outlook(direction=Direction.NEUTRAL, confidence=0.0),
        0.0, _contrib(), _ind(ma20=95.0, ma50=100.0, atr_pct=0.05), _CONFIG, False,
    ))
    assert got["trend"].tone == "warning"
    assert got["volatility"].tone == "warning"
