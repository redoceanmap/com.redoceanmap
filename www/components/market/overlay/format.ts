// 원 단위 금액을 억/만 단위로 축약 — 오버레이 섹션 공용
export const formatMoney = (won: number): string => {
  if (Math.abs(won) >= 1e8) return `${(won / 1e8).toFixed(1)}억원`;
  if (Math.abs(won) >= 1e4) return `${Math.round(won / 1e4).toLocaleString("ko-KR")}만원`;
  return `${Math.round(won).toLocaleString("ko-KR")}원`;
};

export const formatPop = (n: number): string =>
  Math.abs(n) >= 1e4 ? `${(n / 1e4).toFixed(1)}만` : n.toLocaleString("ko-KR");
