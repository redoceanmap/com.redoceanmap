"use client";

import { useEffect, useRef } from "react";
import {
  CandlestickSeries,
  HistogramSeries,
  LineSeries,
  createChart,
  type IChartApi,
  type IPriceLine,
  type ISeriesApi,
  type UTCTimestamp,
} from "lightweight-charts";
import type { PriceBar, StockForecast } from "@/lib/types";

// 한국 관례: 상승 빨강 / 하락 파랑 (StockCard·방향 배지와 동일)
const UP = "#DC2626";
const DOWN = "#2563EB";
const MA20_COLOR = "#D97706";
const MA50_COLOR = "#7C3AED";
const RSI_COLOR = "#0D9488";

type CandleChartProps = {
  bars: PriceBar[]; // ts 오름차순
  support?: number | null;
  resistance?: number | null;
  forecast?: StockForecast | null; // 예측 밴드 — 1d 타임프레임에서만 전달된다
  quotePrice?: number | null; // 준실시간(지연) 현재가 — 마지막 봉 갱신용
};

function sma(bars: PriceBar[], period: number) {
  const out: { time: UTCTimestamp; value: number }[] = [];
  let sum = 0;
  for (let i = 0; i < bars.length; i++) {
    sum += bars[i].close;
    if (i >= period) sum -= bars[i - period].close;
    if (i >= period - 1) {
      out.push({ time: toTime(bars[i].ts), value: sum / period });
    }
  }
  return out;
}

// RSI(14, Wilder 평활) — 백엔드 IndicatorCalculator와 같은 방식
function rsiSeries(bars: PriceBar[], period = 14) {
  const out: { time: UTCTimestamp; value: number }[] = [];
  if (bars.length < period + 1) return out;
  let avgGain = 0;
  let avgLoss = 0;
  for (let i = 1; i <= period; i++) {
    const diff = bars[i].close - bars[i - 1].close;
    if (diff > 0) avgGain += diff;
    else avgLoss -= diff;
  }
  avgGain /= period;
  avgLoss /= period;
  const toRsi = () => (avgLoss === 0 ? 100 : 100 - 100 / (1 + avgGain / avgLoss));
  out.push({ time: toTime(bars[period].ts), value: toRsi() });
  for (let i = period + 1; i < bars.length; i++) {
    const diff = bars[i].close - bars[i - 1].close;
    avgGain = (avgGain * (period - 1) + Math.max(diff, 0)) / period;
    avgLoss = (avgLoss * (period - 1) + Math.max(-diff, 0)) / period;
    out.push({ time: toTime(bars[i].ts), value: toRsi() });
  }
  return out;
}

// 마지막 봉 이후 horizon 거래일(주말 제외)의 미래 타임스탬프
function futureTime(lastTs: string, tradingDays: number): UTCTimestamp {
  const d = new Date(lastTs);
  let added = 0;
  while (added < tradingDays) {
    d.setDate(d.getDate() + 1);
    if (d.getDay() !== 0 && d.getDay() !== 6) added++;
  }
  return (d.getTime() / 1000) as UTCTimestamp;
}

const toTime = (ts: string) => (new Date(ts).getTime() / 1000) as UTCTimestamp;

type ChartRefs = {
  chart: IChartApi;
  candles: ISeriesApi<"Candlestick">;
  volume: ISeriesApi<"Histogram">;
  ma20: ISeriesApi<"Line">;
  ma50: ISeriesApi<"Line">;
  rsi: ISeriesApi<"Line">;
  bandLines: ISeriesApi<"Line">[];
  priceLines: IPriceLine[];
};

export default function CandleChart({ bars, support, resistance, forecast, quotePrice }: CandleChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const refs = useRef<ChartRefs | null>(null);
  // setData가 봉을 원복해도 최신 quote를 재적용할 수 있게 ref로 보관
  const quoteRef = useRef<number | null>(null);
  quoteRef.current = quotePrice ?? null;
  // 저장 봉에 없는 "오늘" 임시 봉 — quote 갱신 간 open/고저 유지용
  const provisionalRef = useRef<{ time: number; open: number; high: number; low: number } | null>(null);
  const prevBarsRef = useRef<PriceBar[] | null>(null);

  // 지연 현재가 반영 — 마지막 저장 봉이 오늘 봉일 때만 병합하고,
  // 오늘 봉이 아직 없으면(야간 수집 전) 임시 봉을 덧붙인다. 과거 봉은 왜곡하지 않는다.
  const applyQuote = (r: ChartRefs) => {
    const price = quoteRef.current;
    if (!price || bars.length === 0) return;
    const last = bars[bars.length - 1];
    const lastDay = Math.floor(new Date(last.ts).getTime() / 86_400_000);
    const today = Math.floor(Date.now() / 86_400_000);
    if (today === lastDay) {
      r.candles.update({
        time: toTime(last.ts),
        open: last.open,
        high: Math.max(last.high, price),
        low: Math.min(last.low, price),
        close: price,
      });
    } else if (today > lastDay) {
      const dow = new Date().getUTCDay();
      if (dow === 0 || dow === 6) return; // 주말 — 유령 봉 방지
      const time = (today * 86_400) as UTCTimestamp;
      const prev = provisionalRef.current?.time === today * 86_400 ? provisionalRef.current : null;
      const bar = {
        time,
        open: prev?.open ?? price,
        high: Math.max(prev?.high ?? price, price),
        low: Math.min(prev?.low ?? price, price),
        close: price,
      };
      provisionalRef.current = { time: today * 86_400, open: bar.open, high: bar.high, low: bar.low };
      r.candles.update(bar);
    }
  };

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const chart = createChart(el, {
      autoSize: true,
      layout: {
        background: { color: "transparent" },
        textColor: "#6B7280",
        fontFamily:
          "'Pretendard Variable', Pretendard, -apple-system, BlinkMacSystemFont, system-ui, sans-serif",
        panes: { separatorColor: "#EBE8DF", enableResize: false },
      },
      grid: {
        vertLines: { color: "rgba(235, 232, 223, 0.6)" },
        horzLines: { color: "rgba(235, 232, 223, 0.6)" },
      },
      rightPriceScale: { borderColor: "#EBE8DF" },
      timeScale: { borderColor: "#EBE8DF", timeVisible: true },
      crosshair: { horzLine: { labelBackgroundColor: "#991B1B" }, vertLine: { labelBackgroundColor: "#991B1B" } },
    });

    const candles = chart.addSeries(CandlestickSeries, {
      upColor: UP,
      downColor: DOWN,
      wickUpColor: UP,
      wickDownColor: DOWN,
      borderVisible: false,
    });
    const volume = chart.addSeries(HistogramSeries, {
      priceScaleId: "volume",
      priceFormat: { type: "volume" },
      priceLineVisible: false,
      lastValueVisible: false,
    });
    chart.priceScale("volume").applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } });
    const lineDefaults = { lineWidth: 1, priceLineVisible: false, lastValueVisible: false, crosshairMarkerVisible: false } as const;
    const ma20 = chart.addSeries(LineSeries, { color: MA20_COLOR, ...lineDefaults });
    const ma50 = chart.addSeries(LineSeries, { color: MA50_COLOR, ...lineDefaults });

    // RSI 서브차트 — pane 1
    const rsi = chart.addSeries(LineSeries, { color: RSI_COLOR, ...lineDefaults }, 1);
    rsi.createPriceLine({ price: 70, color: "#D1D5DB", lineWidth: 1, lineStyle: 2, axisLabelVisible: true, title: "" });
    rsi.createPriceLine({ price: 30, color: "#D1D5DB", lineWidth: 1, lineStyle: 2, axisLabelVisible: true, title: "" });
    chart.panes()[1]?.setHeight(80);

    refs.current = { chart, candles, volume, ma20, ma50, rsi, bandLines: [], priceLines: [] };
    return () => {
      chart.remove();
      refs.current = null;
    };
  }, []);

  useEffect(() => {
    const r = refs.current;
    if (!r) return;

    r.candles.setData(
      bars.map((b) => ({ time: toTime(b.ts), open: b.open, high: b.high, low: b.low, close: b.close })),
    );
    r.volume.setData(
      bars.map((b) => ({
        time: toTime(b.ts),
        value: b.volume,
        color: b.close >= b.open ? "rgba(220, 38, 38, 0.28)" : "rgba(37, 99, 235, 0.28)",
      })),
    );
    r.ma20.setData(sma(bars, 20));
    r.ma50.setData(sma(bars, 50));
    r.rsi.setData(rsiSeries(bars));

    r.priceLines.forEach((line) => r.candles.removePriceLine(line));
    r.priceLines = [];
    const lineOptions = { lineWidth: 1, lineStyle: 2, axisLabelVisible: true } as const;
    if (support) {
      r.priceLines.push(
        r.candles.createPriceLine({ price: support, color: DOWN, title: "지지", ...lineOptions }),
      );
    }
    if (resistance) {
      r.priceLines.push(
        r.candles.createPriceLine({ price: resistance, color: UP, title: "저항", ...lineOptions }),
      );
    }

    // 예측 밴드 — 마지막 봉에서 horizon 거래일 뒤로 분위수(또는 ATR 콘)를 점선 투영
    r.bandLines.forEach((s) => r.chart.removeSeries(s));
    r.bandLines = [];
    const band = forecast?.band;
    if (band && bars.length > 0) {
      const lastBar = bars[bars.length - 1];
      const start = { time: toTime(lastBar.ts), value: lastBar.close };
      const end = futureTime(lastBar.ts, forecast.horizon_days);
      const targets: { pct: number; color: string; label: string }[] =
        band.source === "quantile"
          ? [
              { pct: band.q75_pct, color: UP, label: "상위 25%" },
              { pct: band.median_pct, color: "#6B7280", label: "중앙값" },
              { pct: band.q25_pct, color: DOWN, label: "하위 25%" },
            ]
          : [
              { pct: band.q75_pct, color: UP, label: "예상 상단" },
              { pct: band.q25_pct, color: DOWN, label: "예상 하단" },
            ];
      for (const t of targets) {
        const series = r.chart.addSeries(LineSeries, {
          color: t.color,
          lineWidth: 1,
          lineStyle: 2,
          priceLineVisible: false,
          lastValueVisible: true,
          crosshairMarkerVisible: false,
          title: `${t.label} ${t.pct >= 0 ? "+" : ""}${(t.pct * 100).toFixed(1)}%`,
        });
        series.setData([start, { time: end, value: lastBar.close * (1 + t.pct) }]);
        r.bandLines.push(series);
      }
    }

    // setData가 봉을 원복하므로 quote를 재적용한다(임시 봉 추적은 리셋)
    provisionalRef.current = null;
    applyQuote(r);

    // 줌 리셋은 봉 데이터 자체가 바뀔 때만 — forecast/analyze 지연 도착이 뷰를 뺏지 않게
    if (prevBarsRef.current !== bars) {
      r.chart.timeScale().fitContent();
      prevBarsRef.current = bars;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [bars, support, resistance, forecast]);

  // 준실시간 현재가 — 마지막 봉만 갱신(전체 setData 없이 깜빡임 방지)
  useEffect(() => {
    const r = refs.current;
    if (r) applyQuote(r);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [quotePrice, bars]);

  return (
    <div className="relative flex-1 min-h-0">
      <div ref={containerRef} className="absolute inset-0" />
      <div className="absolute left-3 top-2 z-10 flex items-center gap-3 text-[11px] text-foreground-muted pointer-events-none">
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-0.5" style={{ background: MA20_COLOR }} /> MA20
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-0.5" style={{ background: MA50_COLOR }} /> MA50
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-0.5" style={{ background: RSI_COLOR }} /> RSI(14)
        </span>
        {forecast?.band && (
          <span>
            예측 범위: {forecast.band.source === "quantile" ? "과거 실적 분위수" : "변동성(ATR) 기반"}
          </span>
        )}
      </div>
      {/* lightweight-charts 라이선스 고지 */}
      <a
        href="https://www.tradingview.com/"
        target="_blank"
        rel="noopener noreferrer"
        className="absolute right-2 bottom-1 z-10 text-[10px] text-foreground-muted/70 hover:text-foreground-muted"
      >
        Charts by TradingView
      </a>
    </div>
  );
}
