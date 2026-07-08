"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, MapPin, TrendingUp, Users, Store, Clock, ChevronUp } from "lucide-react";
import MapView from "@/components/seoul/MapView";
import { useChatStore } from "@/lib/store";
import type { Area } from "@/lib/mockApi";

function StatRow({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <p className="text-xs text-foreground-muted">{label}</p>
      <p className="text-sm font-medium">{value}</p>
      {sub && <p className="text-xs text-foreground-muted leading-snug">{sub}</p>}
    </div>
  );
}

function Section({ icon: Icon, title, children }: { icon: any; title: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-foreground-muted uppercase tracking-wide">
        <Icon size={13} strokeWidth={2} />
        {title}
      </div>
      <div className="flex flex-col gap-3 pl-0.5">{children}</div>
    </div>
  );
}

function AreaDetail({ area }: { area: Area }) {
  return (
    <>
      <div className="p-5 border-b border-border">
        <p className="text-xs text-foreground-muted mb-1">{area.category}</p>
        <h2 className="text-lg font-semibold mb-2">{area.name}</h2>
        <p className="text-sm text-foreground/80 leading-relaxed">{area.reason}</p>
        {area.stats.hasRealData && (
          <p className="text-xs text-brand mt-2">{area.stats.dataSource}</p>
        )}
      </div>

      <div className="p-5 flex flex-col gap-5">
        <Section icon={TrendingUp} title="수익성">
          <StatRow label="점포당 월 매출 (추정)" value={area.stats.monthlyRevenueText} sub={area.stats.revenueSourceText} />
          <StatRow label="매출 패턴" value={area.stats.weekdayText} />
        </Section>
        <div className="border-t border-border" />
        <Section icon={Store} title="점포 현황">
          <StatRow label="영업 점포" value={area.stats.storeCountText} />
          <StatRow label="폐업률" value={area.stats.closureRateText} />
          <StatRow label="개업률" value={area.stats.openingRateText} />
          <StatRow label="프랜차이즈" value={area.stats.franchiseText} />
        </Section>
        <div className="border-t border-border" />
        <Section icon={Users} title="유동인구">
          <StatRow label="일평균 유동인구" value={area.stats.footTrafficText} />
          <StatRow label="주요 연령대" value={area.stats.topAgeText} />
          <StatRow label="피크 시간대" value={area.stats.peakTimeText} />
        </Section>
        <div className="border-t border-border" />
        <Section icon={Clock} title="상권 변화">
          <StatRow label="상권 변화 지표" value={area.stats.changeText} />
          <StatRow label="영업 지속성" value={area.stats.operatingMonthsText} />
        </Section>
      </div>
    </>
  );
}

export default function MapPage() {
  const recommendations = useChatStore((s) => s.recommendations);
  // REACT_RULES 패턴 B: selectedId + sheetOpen 객체로 압축
  const [ui, setUi] = useState({
    selectedId: recommendations[0]?.id ?? null,
    sheetOpen: false,
  });

  const selected = recommendations.find((a) => a.id === ui.selectedId) ?? null;

  const handleSelect = (id: string) => {
    setUi({ selectedId: id, sheetOpen: true });
  };

  if (recommendations.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4 text-center px-6">
        <MapPin size={36} className="text-foreground-muted" strokeWidth={1.5} />
        <p className="text-foreground-muted text-sm">
          아직 추천받은 상권이 없어요.
          <br />
          홈에서 프롬프트를 입력해보세요.
        </p>
        <Link
          href="/"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-brand text-white text-sm font-medium hover:bg-brand-deep transition-colors"
        >
          <ArrowLeft size={15} strokeWidth={2.25} />
          홈으로
        </Link>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col min-h-0 px-6 pb-6">
      {/* 상단 헤더 */}
      <div className="flex items-center justify-between mb-4">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-sm text-foreground-muted hover:text-foreground"
        >
          <ArrowLeft size={15} strokeWidth={1.75} />
          홈으로
        </Link>
        <div className="text-xs text-foreground-muted">추천 상권 {recommendations.length}곳</div>
      </div>

      {/* 데스크탑: 지도 + 사이드바 나란히 */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-4 min-h-0">
        <div className="min-h-[500px] lg:min-h-0">
          <MapView areas={recommendations} selectedId={ui.selectedId} onSelect={handleSelect} />
        </div>

        {/* 데스크탑 전용 사이드바 */}
        <aside className="hidden lg:flex bg-surface border border-border rounded-2xl overflow-y-auto flex-col">
          {selected ? (
            <AreaDetail area={selected} />
          ) : (
            <div className="p-5">
              <p className="text-sm text-foreground-muted">지도에서 상권을 클릭하세요</p>
            </div>
          )}

          <div className="mt-auto p-5 pt-0 flex flex-col gap-2">
            <div className="border-t border-border pt-4">
              {recommendations.map((area) => (
                <button
                  key={area.id}
                  onClick={() => handleSelect(area.id)}
                  className={`w-full text-left px-3 py-2.5 rounded-xl border transition-colors mb-1.5 ${
                    area.id === ui.selectedId
                      ? "border-brand bg-brand/5 text-brand"
                      : "border-border hover:border-foreground-muted/40"
                  }`}
                >
                  <p className="text-sm font-medium">{area.name}</p>
                  <p className="text-xs text-foreground-muted">{area.category}</p>
                </button>
              ))}
            </div>
          </div>
        </aside>
      </div>

      {/* 모바일 Bottom Sheet */}
      <div
        className={`lg:hidden fixed left-0 right-0 bottom-14 z-40 transition-transform duration-300 ease-out ${
          ui.sheetOpen ? "translate-y-0" : "translate-y-[calc(100%-4.5rem)]"
        }`}
      >
        {/* 핸들 + collapsed 미리보기 */}
        <button
          type="button"
          aria-label={ui.sheetOpen ? "시트 닫기" : "시트 열기"}
          onClick={() => setUi((prev) => ({ ...prev, sheetOpen: !prev.sheetOpen }))}
          className="w-full bg-surface border border-b-0 border-border rounded-t-2xl px-5 pt-3 pb-4 text-left"
        >
          <div className="flex justify-center mb-3">
            <div className="w-8 h-1 rounded-full bg-border" />
          </div>
          <div className="flex items-center justify-between">
            {selected ? (
              <div>
                <p className="text-xs text-foreground-muted">{selected.category}</p>
                <p className="font-semibold">{selected.name}</p>
              </div>
            ) : (
              <p className="text-sm text-foreground-muted">지도에서 상권을 선택하세요</p>
            )}
            <ChevronUp
              size={18}
              strokeWidth={2}
              className={`text-foreground-muted transition-transform duration-300 ${
                ui.sheetOpen ? "rotate-180" : ""
              }`}
            />
          </div>
        </button>

        {/* 상세 내용 */}
        <div className="bg-surface border border-t-0 border-border max-h-[60vh] overflow-y-auto">
          {selected && <AreaDetail area={selected} />}

          {/* 상권 목록 */}
          <div className="p-5 pt-0 flex flex-col gap-2">
            <div className="border-t border-border pt-4">
              {recommendations.map((area) => (
                <button
                  key={area.id}
                  onClick={() => handleSelect(area.id)}
                  className={`w-full text-left px-3 py-2.5 rounded-xl border transition-colors mb-1.5 ${
                    area.id === ui.selectedId
                      ? "border-brand bg-brand/5 text-brand"
                      : "border-border hover:border-foreground-muted/40"
                  }`}
                >
                  <p className="text-sm font-medium">{area.name}</p>
                  <p className="text-xs text-foreground-muted">{area.category}</p>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
