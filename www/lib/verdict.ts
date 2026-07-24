import type { StockAnalyzeResult, StockForecast } from "@/lib/types";

// 확률이 기준선을 이 정도는 넘어야 "평소와 다르다"고 말한다
const EDGE_MIN_PP = 3;

const DIRECTION_WORD: Record<StockAnalyzeResult["direction"], string> = {
  UP: "상승",
  DOWN: "하락",
  NEUTRAL: "중립",
};

/** 결론 한 줄 — 방향 신호와 과거 통계를 합쳐 하나로 말한다.
 *  판정·확률·확신도를 따로 띄우면 "상승 36%" vs "평소와 다르지 않음"처럼 서로 반박한다.
 *  히어로·StageSummary·챗 카드 3면이 같은 결론을 쓰도록 단일 소스로 둔다. */
export function verdict(
  analyze: StockAnalyzeResult,
  forecast?: StockForecast,
): { headline: string; detail: string } {
  const p = forecast?.probability;
  const edgePp = p ? Math.round(p.up_rate * 100) - Math.round(p.baseline_up_rate * 100) : null;
  const word = DIRECTION_WORD[analyze.direction];

  if (analyze.direction === "NEUTRAL") {
    return {
      headline: "지금은 방향을 말하기 어렵습니다",
      detail: "지표들이 서로 상쇄돼 한쪽으로 기울지 않았습니다.",
    };
  }
  if (edgePp === null || !p?.ready || Math.abs(edgePp) < EDGE_MIN_PP) {
    return {
      headline: `${word} 쪽 신호가 있지만, 근거는 약합니다`,
      detail:
        edgePp === null
          ? "과거 통계로 검증할 표본이 아직 없습니다."
          : `과거 같은 신호일 때 상승 비율이 평소와 사실상 같았습니다(차이 ${edgePp >= 0 ? "+" : ""}${edgePp}%p).`,
    };
  }
  return {
    headline: `${word} 쪽 신호이고, 과거 통계도 평소보다 ${edgePp >= 0 ? "+" : ""}${edgePp}%p 높았습니다`,
    detail: `표본 ${p.sample_size}회 · 95% 구간 ${Math.round(p.ci_low * 100)}~${Math.round(p.ci_high * 100)}%.`,
  };
}

/** 신호 세기 — "확신도 36%"는 초보자가 확률로 오독한다. 확률이 아니라는 게 드러나는 표기로 바꾼다. */
export function strength(analyze: StockAnalyzeResult): string {
  const score = Math.abs(analyze.score ?? 0);
  const threshold = analyze.up_threshold ?? 0.3;
  if (score < threshold) return "약";
  if (score < threshold * 2) return "보통";
  return "강";
}
