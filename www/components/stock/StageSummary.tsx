"use client";

import { ChevronDown, Eye, Minus, TrendingDown, TrendingUp } from "lucide-react";
import type { StockAnalyzeResult, StockForecast } from "@/lib/types";
import { formatPrice } from "@/lib/currency";
import InsightList from "@/components/common/InsightList";

// 확률이 기준선을 이 정도는 넘어야 "평소와 다르다"고 말한다
const EDGE_MIN_PP = 3;
// 초보자가 체감할 기준 투자금 — ATR%를 금액으로 옮길 때 쓴다
const RISK_BASE_KRW = 1_000_000;

type Props = {
  symbol: string;
  price?: number;
  analyze?: StockAnalyzeResult;
  forecast?: StockForecast;
  expert: boolean;
  onToggleExpert: () => void;
};

const DIRECTION = {
  UP: { word: "상승", icon: TrendingUp, className: "text-red-600 bg-red-50 border-red-200" },
  DOWN: { word: "하락", icon: TrendingDown, className: "text-blue-600 bg-blue-50 border-blue-200" },
  NEUTRAL: { word: "중립", icon: Minus, className: "text-foreground-muted bg-surface border-border" },
} as const;

/** 결론 한 줄 — 방향 신호와 과거 통계를 합쳐 하나로 말한다.
 *  판정·확률·확신도를 따로 띄우면 "상승 36%" vs "평소와 다르지 않음"처럼 서로 반박한다. */
function verdict(analyze: StockAnalyzeResult, forecast?: StockForecast) {
  const p = forecast?.probability;
  const edgePp = p ? Math.round(p.up_rate * 100) - Math.round(p.baseline_up_rate * 100) : null;
  const word = DIRECTION[analyze.direction].word;

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
function strength(analyze: StockAnalyzeResult) {
  const score = Math.abs(analyze.score ?? 0);
  const threshold = analyze.up_threshold ?? 0.3;
  if (score < threshold) return "약";
  if (score < threshold * 2) return "보통";
  return "강";
}

/** 지지 ─ 현재 ─ 저항 위치. 예측이 아니라 관측된 사실이라 그대로 보여줘도 정직하다. */
function PricePosition({ analyze, price, symbol }: { analyze: StockAnalyzeResult; price: number; symbol: string }) {
  const { support, resistance } = analyze;
  if (!(resistance > support)) return null;
  const ratio = Math.max(0, Math.min(1, (price - support) / (resistance - support)));

  return (
    <div>
      <div className="flex items-baseline justify-between text-[10px] text-foreground-muted">
        <span>지지 {formatPrice(support, symbol)}</span>
        <span>저항 {formatPrice(resistance, symbol)}</span>
      </div>
      <div className="relative mt-1 h-1.5 rounded-full bg-gradient-to-r from-blue-200 via-border to-red-200">
        <div
          className="absolute top-1/2 -translate-y-1/2 w-2.5 h-2.5 rounded-full bg-foreground border-2 border-background shadow"
          style={{ left: `calc(${ratio * 100}% - 5px)` }}
        />
      </div>
      <p className="mt-1 text-[11px] text-foreground-muted">
        60일 등락 구간의 <b className="font-semibold text-foreground">{Math.round(ratio * 100)}% 지점</b>에
        있습니다 {ratio <= 0.25 ? "(바닥권)" : ratio >= 0.75 ? "(고점권)" : "(중간)"}
      </p>
    </div>
  );
}

/** 변동성·예측 범위를 금액으로. "ATR 12.5%"보다 "100만원이면 하루 ±12.5만원"이 훨씬 읽힌다. */
function RiskSummary({
  analyze,
  forecast,
  price,
  symbol,
}: {
  analyze: StockAnalyzeResult;
  forecast?: StockForecast;
  price: number;
  symbol: string;
}) {
  const daily = Math.round(analyze.atr_pct * RISK_BASE_KRW);
  const band = forecast?.band;

  return (
    <div className="text-[11px] leading-relaxed">
      <p>
        하루 평균 <b className="font-semibold">±{(analyze.atr_pct * 100).toFixed(1)}%</b> 움직입니다 —
        100만원이면 하루 <b className="font-semibold">±{daily.toLocaleString("ko-KR")}원</b>.
      </p>
      {band && (
        <p className="mt-0.5">
          {forecast!.horizon_days}일 뒤 예상 범위{" "}
          <b className="font-semibold" style={{ color: "#2563EB" }}>
            {formatPrice(price * (1 + band.q25_pct), symbol)}
          </b>{" "}
          ~{" "}
          <b className="font-semibold" style={{ color: "#DC2626" }}>
            {formatPrice(price * (1 + band.q75_pct), symbol)}
          </b>
          <span className="text-foreground-muted"> (과거 통계이며 보장이 아닙니다)</span>
        </p>
      )}
    </div>
  );
}

export default function StageSummary({
  symbol,
  price,
  analyze,
  forecast,
  expert,
  onToggleExpert,
}: Props) {
  if (!analyze) return null;
  const current = price ?? analyze.price;
  const { headline, detail } = verdict(analyze, forecast);
  const meta = DIRECTION[analyze.direction] ?? DIRECTION.NEUTRAL;
  const DirectionIcon = meta.icon;
  // 판정에 실제로 들어간 신호 수 — 가중치 0인 참고 지표는 세지 않는다
  const usedSignals = (analyze.signals ?? []).filter((s) => s.weight !== 0 && s.contribution !== 0).length;
  const p = forecast?.probability;

  return (
    <div className="shrink-0 px-4 py-2.5 border-b border-border">
      <div className="flex items-start gap-2">
        <span className={`shrink-0 inline-flex items-center gap-1 px-2 py-1 rounded-full border text-[11px] font-medium ${meta.className}`}>
          <DirectionIcon size={12} strokeWidth={2} />
          신호 {strength(analyze)}
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold leading-snug">{headline}</p>
          <p className="text-[11px] text-foreground-muted leading-snug">
            {detail} 판정에 쓰인 신호 {usedSignals}개.
          </p>
        </div>
        <button
          type="button"
          onClick={onToggleExpert}
          className="shrink-0 inline-flex items-center gap-1 px-2 h-6 rounded-md border border-border text-[10px] text-foreground-muted hover:bg-black/5 transition-colors"
          aria-pressed={expert}
        >
          <Eye size={11} strokeWidth={2} />
          {expert ? "간단히" : "자세히"}
        </button>
      </div>

      <div className="mt-2 grid gap-x-6 gap-y-2 sm:grid-cols-2">
        <PricePosition analyze={analyze} price={current} symbol={symbol} />
        <RiskSummary analyze={analyze} forecast={forecast} price={current} symbol={symbol} />
      </div>

      {expert && (
        <div className="mt-2 pt-2 border-t border-border text-[11px] text-foreground-muted">
          종합 점수 {analyze.score !== undefined ? analyze.score.toFixed(2) : "—"} (기준 ±
          {(analyze.up_threshold ?? 0.3).toFixed(2)}) · 확신도 {Math.round(analyze.confidence * 100)}%
          {p && (
            <>
              {" · "}상승 확률 {Math.round(p.up_rate * 100)}% · 평소 {Math.round(p.baseline_up_rate * 100)}%
              {" · "}표본 {p.sample_size}회 중 {p.hits}회 · 95% 구간{" "}
              {Math.round(p.ci_low * 100)}~{Math.round(p.ci_high * 100)}%
              {!p.ready && " · 표본 부족(참고용)"}
            </>
          )}
        </div>
      )}

      {forecast && forecast.insights.length > 0 && (
        <details className="mt-1.5 group">
          <summary className="flex items-center gap-1 text-[11px] text-foreground-muted cursor-pointer list-none select-none">
            <ChevronDown size={12} className="transition-transform group-open:rotate-180" />
            근거 보기 — 과거 통계이며 미래를 보장하지 않습니다
          </summary>
          <div className="mt-1.5 pl-1">
            <InsightList insights={forecast.insights} />
          </div>
        </details>
      )}
    </div>
  );
}
