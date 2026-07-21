import { AlertTriangle, Lightbulb, ThumbsUp } from "lucide-react";
import type { Insight } from "@/lib/types";

const TONE = {
  positive: { icon: ThumbsUp, className: "text-emerald-600" },
  neutral: { icon: Lightbulb, className: "text-foreground-muted" },
  warning: { icon: AlertTriangle, className: "text-amber-600" },
} as const;

// 규칙 기반 해석 문장 리스트 — market·stock 공용
export default function InsightList({ insights }: { insights: Insight[] }) {
  if (insights.length === 0) return null;
  return (
    <ul className="flex flex-col gap-1.5">
      {insights.map((i) => {
        const tone = TONE[i.tone] ?? TONE.neutral;
        const Icon = tone.icon;
        return (
          <li key={i.key} className="flex items-start gap-2 text-sm leading-snug">
            <Icon size={14} strokeWidth={2} className={`mt-0.5 shrink-0 ${tone.className}`} />
            <span>{i.text}</span>
          </li>
        );
      })}
    </ul>
  );
}
