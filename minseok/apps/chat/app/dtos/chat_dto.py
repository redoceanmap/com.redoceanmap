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


class AskResponse(BaseModel):
    text: str
    recommendations: list[AreaRecommendation]
    conversationId: int
    stock: StockCard | None = None
