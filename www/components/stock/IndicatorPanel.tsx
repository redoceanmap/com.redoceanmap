"use client";

import type { StockAnalyzeResult } from "@/lib/types";
import { formatPrice } from "@/lib/currency";
import InsightList from "@/components/common/InsightList";
import SignalBreakdown from "./SignalBreakdown";

const fmt = (v: number, digits = 2) =>
  v.toLocaleString("ko-KR", { maximumFractionDigits: digits });

// 백엔드 stock_narrator.py와 같은 임계값 — 화면 라벨과 해설 문장이 어긋나지 않게 맞춘다
const RSI_OVERSOLD = 30;
const RSI_OVERBOUGHT = 70;
const BB_LOW = 0.2;
const BB_HIGH = 0.8;
const VOLUME_SURGE = 1.5;
const VOLUME_QUIET = 0.7;
const MOMENTUM_MIN = 0.15;
const ATR_HIGH = 4.0;

type Tone = "up" | "down" | "flat";

type Stat = {
  label: string;
  value: string;
  hint: string;
  tone: Tone;
  // 0~1 상대 위치 — 상·하한이 정해진 지표에만 게이지를 그린다
  gauge?: { position: number; marks: number[] };
};

const TONE_TEXT: Record<Tone, string> = {
  up: "text-red-600",
  down: "text-blue-600",
  flat: "text-foreground-muted",
};
const TONE_BG: Record<Tone, string> = {
  up: "bg-red-500",
  down: "bg-blue-500",
  flat: "bg-foreground-muted",
};

const clamp01 = (v: number) => Math.max(0, Math.min(1, v));

function buildStats(a: StockAnalyzeResult, symbol: string): Stat[] {
  const trendGap = a.ma50 > 0 ? (a.ma20 - a.ma50) / a.ma50 : 0;
  const price = (v: number) => formatPrice(v, symbol);

  return [
    {
      label: "RSI(14)",
      value: fmt(a.rsi, 1),
      hint: a.rsi <= RSI_OVERSOLD ? "과매도 — 반등 여지" : a.rsi >= RSI_OVERBOUGHT ? "과열 — 조정 주의" : "중립 구간",
      tone: a.rsi <= RSI_OVERSOLD ? "down" : a.rsi >= RSI_OVERBOUGHT ? "up" : "flat",
      gauge: { position: clamp01(a.rsi / 100), marks: [0.3, 0.7] },
    },
    {
      label: "볼린저 %B",
      value: fmt(a.bb_percent_b),
      hint:
        a.bb_percent_b <= BB_LOW
          ? "밴드 하단 — 단기 과매도권"
          : a.bb_percent_b >= BB_HIGH
            ? "밴드 상단 — 단기 과열권"
            : "밴드 중앙",
      tone: a.bb_percent_b <= BB_LOW ? "down" : a.bb_percent_b >= BB_HIGH ? "up" : "flat",
      gauge: { position: clamp01(a.bb_percent_b), marks: [BB_LOW, BB_HIGH] },
    },
    {
      label: "거래량비 (5/20일)",
      value: `${fmt(a.volume_ratio)}x`,
      hint:
        a.volume_ratio >= VOLUME_SURGE
          ? "평소보다 급증"
          : a.volume_ratio <= VOLUME_QUIET
            ? "평소보다 한산"
            : "평소 수준",
      tone: a.volume_ratio >= VOLUME_SURGE ? "up" : a.volume_ratio <= VOLUME_QUIET ? "down" : "flat",
      // 1.0(평소)이 한가운데 오도록 0~2배 구간에 놓는다
      gauge: { position: clamp01(a.volume_ratio / 2), marks: [VOLUME_QUIET / 2, VOLUME_SURGE / 2] },
    },
    {
      label: "OBV 기울기",
      value: fmt(a.obv_slope, 3),
      hint: a.obv_slope > 0 ? "자금 유입 우위" : a.obv_slope < 0 ? "자금 유출 우위" : "수급 중립",
      tone: a.obv_slope > 0 ? "up" : a.obv_slope < 0 ? "down" : "flat",
    },
    {
      label: "12-1 모멘텀",
      value: `${fmt(a.momentum_12_1 * 100, 1)}%`,
      hint:
        a.momentum_12_1 >= MOMENTUM_MIN
          ? "중장기 상승 추세"
          : a.momentum_12_1 <= -MOMENTUM_MIN
            ? "중장기 하락 추세"
            : "중장기 방향성 약함",
      tone: a.momentum_12_1 >= MOMENTUM_MIN ? "up" : a.momentum_12_1 <= -MOMENTUM_MIN ? "down" : "flat",
    },
    {
      label: "ATR (변동성)",
      value: `${fmt(a.atr_pct * 100, 1)}%`,
      hint: a.atr_pct * 100 >= ATR_HIGH ? "급등락 주의" : "변동성 보통",
      tone: a.atr_pct * 100 >= ATR_HIGH ? "up" : "flat",
    },
    {
      label: "20일 이평",
      value: price(a.ma20),
      hint:
        trendGap >= 0.02
          ? `50일선 위 +${fmt(trendGap * 100, 1)}% (정배열)`
          : trendGap <= -0.02
            ? `50일선 아래 ${fmt(trendGap * 100, 1)}% (역배열)`
            : "50일선과 근접",
      tone: trendGap >= 0.02 ? "up" : trendGap <= -0.02 ? "down" : "flat",
    },
    {
      label: "50일 이평",
      value: price(a.ma50),
      hint: "중기 추세 기준선",
      tone: "flat",
    },
    {
      label: "지지선",
      value: price(a.support),
      hint: `현재가 대비 ${fmt((a.support / a.price - 1) * 100, 1)}%`,
      tone: "down",
    },
    {
      label: "저항선",
      value: price(a.resistance),
      hint: `현재가 대비 +${fmt((a.resistance / a.price - 1) * 100, 1)}%`,
      tone: "up",
    },
  ];
}

export default function IndicatorPanel({
  analyze,
  symbol,
}: {
  analyze?: StockAnalyzeResult;
  symbol: string;
}) {
  if (!analyze) {
    return (
      <div className="p-4 grid grid-cols-2 gap-2">
        {Array.from({ length: 8 }, (_, i) => (
          <div key={i} className="skeleton h-14 rounded-lg" />
        ))}
      </div>
    );
  }

  const stats = buildStats(analyze, symbol);

  return (
    <div className="p-4 flex flex-col gap-3">
      <SignalBreakdown analyze={analyze} />

      {analyze.insights && analyze.insights.length > 0 && (
        <div className="bg-surface border border-border rounded-lg px-3 py-2.5">
          <InsightList insights={analyze.insights} />
        </div>
      )}

      <div className="grid grid-cols-2 gap-2">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-surface border border-border rounded-lg px-3 py-2.5">
            <div className="text-[11px] text-foreground-muted">{stat.label}</div>
            <div className="text-sm font-semibold mt-0.5 tabular-nums">{stat.value}</div>
            {stat.gauge && (
              <div className="relative mt-1.5 h-1 rounded-full bg-border/70">
                {stat.gauge.marks.map((mark) => (
                  <div
                    key={mark}
                    className="absolute inset-y-0 w-px bg-foreground-muted/50"
                    style={{ left: `${mark * 100}%` }}
                  />
                ))}
                <div
                  className={`absolute top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full ${TONE_BG[stat.tone]}`}
                  style={{ left: `calc(${stat.gauge.position * 100}% - 3px)` }}
                />
              </div>
            )}
            <div className={`mt-1 text-[10px] leading-tight ${TONE_TEXT[stat.tone]}`}>{stat.hint}</div>
          </div>
        ))}
      </div>

      <div className="bg-surface border border-border rounded-lg px-3 py-2.5">
        <div className="text-[11px] text-foreground-muted">뉴스 감성</div>
        <div className="text-sm font-semibold mt-0.5">
          {analyze.sentiment_label}{" "}
          <span className="text-xs font-normal text-foreground-muted">
            ({analyze.sentiment > 0 ? "+" : ""}{fmt(analyze.sentiment)})
          </span>
        </div>
      </div>

      <p className="text-[11px] text-foreground-muted leading-relaxed">
        지연 시세 기반 참고 지표입니다. 매매 지시가 아니며 투자 판단과 책임은 본인에게 있습니다.
      </p>
    </div>
  );
}
