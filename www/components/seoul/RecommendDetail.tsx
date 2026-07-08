"use client";

import type { Area } from "@/lib/mockApi";
import { Banknote, TrendingDown, Users, ArrowRight } from "lucide-react";

type Props = {
  area: Area | null;
};

export default function RecommendDetail({ area }: Props) {
  if (!area) {
    return (
      <div className="h-full flex items-center justify-center text-sm text-foreground-muted px-6 text-center">
        왼쪽 지도에서 동네를 골라보세요
      </div>
    );
  }

  const items = [
    { icon: Banknote, label: "추정 매출", text: area.stats.monthlyRevenueText },
    { icon: TrendingDown, label: "폐업률", text: area.stats.closureRateText },
    { icon: Users, label: "유동인구", text: area.stats.footTrafficText },
  ];

  return (
    <div className="h-full flex flex-col p-6">
      <div className="mb-1 text-xs text-foreground-muted">{area.category}</div>
      <h2 className="text-2xl font-semibold tracking-tight mb-3">
        {area.name}
      </h2>
      <p className="text-sm text-foreground/80 leading-relaxed mb-6">
        {area.reason}
      </p>

      <div className="flex flex-col gap-3">
        {items.map(({ icon: Icon, label, text }) => (
          <div
            key={label}
            className="bg-surface border border-border rounded-xl p-4"
          >
            <div className="flex items-center gap-2 text-xs text-foreground-muted mb-1.5">
              <Icon size={14} strokeWidth={1.75} className="text-brand" />
              {label}
            </div>
            <p className="text-sm text-foreground">{text}</p>
          </div>
        ))}
      </div>

      <div className="mt-auto pt-6">
        <button className="w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-full bg-brand text-white text-sm font-medium hover:bg-brand-deep transition-colors">
          이 동네 더 알아볼래요
          <ArrowRight size={15} strokeWidth={2.25} />
        </button>
      </div>
    </div>
  );
}
