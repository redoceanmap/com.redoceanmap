// 티커로 통화를 정한다 — 한국 6자리(거래소 접미 포함)는 원, 그 외는 달러.
// 백엔드 chat 컨텍스트(_currency_unit)와 같은 규칙이다.
export const currencyUnit = (symbol: string): "원" | "달러" => {
  const base = symbol.split(".")[0];
  return base.length === 6 && /^\d+$/.test(base) ? "원" : "달러";
};

export const formatPrice = (value: number, symbol: string): string =>
  `${value.toLocaleString("ko-KR", { maximumFractionDigits: 2 })}${currencyUnit(symbol)}`;
