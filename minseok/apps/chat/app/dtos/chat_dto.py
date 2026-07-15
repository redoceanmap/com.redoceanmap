from pydantic import BaseModel


class AreaStats(BaseModel):
    monthlyRevenueText: str
    revenueSourceText: str
    weekdayText: str
    storeCountText: str
    closureRateText: str
    openingRateText: str
    franchiseText: str
    footTrafficText: str
    topAgeText: str
    peakTimeText: str
    changeText: str
    operatingMonthsText: str
    dataSource: str
    hasRealData: bool


class AreaRecommendation(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    category: str
    reason: str
    stats: AreaStats


class StockCard(BaseModel):
    """주식 답변에 곁들이는 구조화 카드 데이터(프론트 렌더링용)."""

    symbol: str
    price: float
    direction: str        # UP | DOWN | NEUTRAL
    confidence: float
    rsi: float
    ma20: float
    ma50: float
    support: float
    resistance: float
    sentimentLabel: str
    headlines: list[str]
    atrPct: float = 0.0             # ATR(14)/종가 — 일 변동성 비율
    bbPercentB: float = 0.5         # 볼린저 %B (0=하단, 1=상단)
    volumeRatio: float = 1.0        # 최근 5일 평균 거래량 / 20일 평균
    obvSlope: float = 0.0           # OBV 20일 정규화 기울기 (수급 방향)
    momentum12To1: float = 0.0      # 12-1 모멘텀 (이력 부족 시 0.0)
    referenceUpSignal: bool = False # 백테스트 검증 통과 참고 신호 — 확률 아님


class NewsCardItem(BaseModel):
    """market_news 답변에 곁들이는 뉴스 근거 카드 1건(프론트 렌더링용)."""

    title: str
    publishedAt: str | None  # YYYY-MM-DD (발행일 미상이면 None)
    ticker: str | None       # 종목 무관 뉴스면 None
    sentiment: float | None  # -1 ~ +1 (라벨 없으면 None)
    eventType: str | None


class AskResponse(BaseModel):
    text: str
    recommendations: list[AreaRecommendation]
    conversationId: int
    stock: StockCard | None = None
    news: list[NewsCardItem] = []
