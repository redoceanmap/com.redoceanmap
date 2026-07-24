"use client";

import { ChevronDown } from "lucide-react";
import type { StockAnalyzeResult, StockForecast } from "@/lib/types";
import { formatPrice } from "@/lib/currency";
import InsightList from "@/components/common/InsightList";

// 초보자가 체감할 기준 투자금 — ATR%를 금액으로 옮길 때 쓴다
const RISK_BASE_KRW = 1_000_000;

type Props = {
  symbol: string;
  price?: number;
  analyze?: StockAnalyzeResult;
  forecast?: StockForecast;
  expert: boolean;
};

/** 최근 60거래일 최저~최고 안에서 현재가 위치.
 *  "지지/저항"으로 부르지 않는다 — 실제로는 60일 롤링 최저·최고 한 봉일 뿐이고,
 *  그 봉이 창을 벗어나면 시장과 무관하게 값이 점프한다(SNDK 실측: 40거래일간 517→980,
 *  2% 넘는 점프 11회). 예측이 아니라 관측된 구간이라는 뜻이 라벨에 드러나야 한다. */
function PricePosition({ analyze, price, symbol }: { analyze: StockAnalyzeResult; price: number; symbol: string }) {
  const { support, resistance } = analyze;
  if (!(resistance > support)) return null;
  const ratio = Math.max(0, Math.min(1, (price - support) / (resistance - support)));

  return (
    <div>
      <div className="flex items-baseline justify-between text-[10px] text-foreground-muted">
        <span>60일 최저 {formatPrice(support, symbol)}</span>
        <span>60일 최고 {formatPrice(resistance, symbol)}</span>
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
        </p>
      )}
    </div>
  );
}

/** 결론(히어로) 아래 근거 계층 — 현재가 위치·변동성/예상범위, 그리고 자세히 보기의 상세·근거. */
export default function StageSummary({ symbol, price, analyze, forecast, expert }: Props) {
  if (!analyze) return null;
  const current = price ?? analyze.price;
  const p = forecast?.probability;

  return (
    <div className="shrink-0 px-4 py-2.5 border-b border-border">
      <div className="grid gap-x-6 gap-y-2 sm:grid-cols-2">
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
            근거 보기
          </summary>
          <div className="mt-1.5 pl-1">
            <InsightList insights={forecast.insights} />
          </div>
        </details>
      )}
    </div>
  );
}
