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
import type { PriceBar } from "@/lib/types";

// 한국 관례: 상승 빨강 / 하락 파랑 (StockCard·방향 배지와 동일)
const UP = "#DC2626";
const DOWN = "#2563EB";
const MA20_COLOR = "#D97706";
const MA50_COLOR = "#7C3AED";

type CandleChartProps = {
  bars: PriceBar[]; // ts 오름차순
  support?: number | null;
  resistance?: number | null;
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

const toTime = (ts: string) => (new Date(ts).getTime() / 1000) as UTCTimestamp;

type ChartRefs = {
  chart: IChartApi;
  candles: ISeriesApi<"Candlestick">;
  volume: ISeriesApi<"Histogram">;
  ma20: ISeriesApi<"Line">;
  ma50: ISeriesApi<"Line">;
  priceLines: IPriceLine[];
};

export default function CandleChart({ bars, support, resistance }: CandleChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const refs = useRef<ChartRefs | null>(null);

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

    refs.current = { chart, candles, volume, ma20, ma50, priceLines: [] };
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

    r.chart.timeScale().fitContent();
  }, [bars, support, resistance]);

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
