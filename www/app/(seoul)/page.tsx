"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Store,
  Wallet,
  MapPin,
  BarChart3,
  Sparkles,
  TrendingUp,
  CandlestickChart,
  Map as MapIcon,
  ArrowUpRight,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { fetchRecommendations } from "@/lib/api";
import { useChatStore } from "@/lib/store";
import { useUIStore } from "@/lib/uiStore";
import ChatInput from "@/components/seoul/ChatInput";

function getGreeting(hour: number) {
  if (hour < 12) return "좋은 아침이에요";
  if (hour < 18) return "오후예요";
  return "오늘 하루 어땠어요";
}

const quickChips = [
  { icon: Store, label: "업종으로 찾기", prompt: "어떤 업종이 잘 될까요?" },
  { icon: Wallet, label: "예산으로 찾기", prompt: "3000만원으로 시작할 수 있는 곳 알려주세요" },
  { icon: MapPin, label: "동네로 찾기", prompt: "성수동 상권 어때요?" },
  { icon: BarChart3, label: "상권 비교", prompt: "성수동이랑 연남동 비교해주세요" },
  { icon: Sparkles, label: "추천받기", prompt: "지금 가장 핫한 동네 추천해주세요" },
  { icon: TrendingUp, label: "주식 물어보기", prompt: "삼성전자 주가 어때요?" },
];

// 비로그인 기본 카드 — 로그인 시 최근 추천 이력(실데이터)으로 대체된다
const defaultAreas = [
  { name: "성수동", category: "카페·디저트", note: "젊은 손님이 많은 동네" },
  { name: "연남동", category: "베이커리", note: "주말 상권이 강한 동네" },
  { name: "망원동", category: "외식업", note: "동네 단골 장사가 되는 곳" },
  { name: "익선동", category: "야간 상권", note: "밤에 사람이 모이는 곳" },
];

const workspaceCards = [
  {
    href: "/stock",
    icon: CandlestickChart,
    title: "주식 분석",
    desc: "캔들차트 · 지표 · 뉴스 · 펀더멘털",
  },
  {
    href: "/market",
    icon: MapIcon,
    title: "상권 분석",
    desc: "지도 · 매출 추이 · 유동인구 · 점포",
  },
];

export default function HomePage() {
  const router = useRouter();
  const messages = useChatStore((s) => s.messages);
  const isLoading = useChatStore((s) => s.isLoading);
  const sendMessage = useChatStore((s) => s.sendMessage);
  const conversationId = useChatStore((s) => s.conversationId);
  const user = useUIStore((s) => s.user);

  // 답변이 도착하면 의도에 맞는 워크스페이스로 이동 — 마운트 시 이미 있던 메시지는 건너뛴다
  const handledRef = useRef<string | null>(messages[messages.length - 1]?.id ?? null);
  useEffect(() => {
    const last = messages[messages.length - 1];
    if (!last || last.role !== "assistant" || handledRef.current === last.id) return;
    handledRef.current = last.id;
    const cParam = conversationId ? `&c=${conversationId}` : "";
    if (last.stock) {
      router.push(`/stock?symbol=${encodeURIComponent(last.stock.symbol)}${cParam}`);
    } else if (last.recommendations && last.recommendations.length > 0) {
      router.push(`/market?trdar=${last.recommendations[0].id}${cParam}`);
    } else {
      // 시장 뉴스 등 텍스트만 온 경우 — 주식 워크스페이스 채팅에서 이어간다
      router.push(`/stock?${cParam.replace("&", "")}`);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messages]);

  const handleSend = (text: string) => {
    void sendMessage(text);
  };

  // 로그인 사용자는 최근 추천 이력(실데이터) 카드, 비로그인은 기본 카드
  const recentQ = useQuery({
    queryKey: ["recent-recommendations"],
    queryFn: () => fetchRecommendations(8),
    enabled: !!user,
  });
  const seen = new Set<string>();
  const recentAreas = (recentQ.data ?? [])
    .filter((r) => !seen.has(r.trdar_name) && seen.add(r.trdar_name))
    .slice(0, 4);
  const useRecent = recentAreas.length > 0;

  // 시간대별 인사는 마운트 후 계산 — SSR(서버 시각)과 달라 하이드레이션 불일치를 내던 버그 수정
  const [greeting, setGreeting] = useState("안녕하세요");
  useEffect(() => {
    setGreeting(getGreeting(new Date().getHours()));
  }, []);

  return (
    <div className="flex-1 flex justify-center items-center px-6 py-12">
      <div className="w-full max-w-3xl flex flex-col">
        <p className="text-sm text-foreground-muted mb-3">
          {user ? `${greeting}, ${user.name}님` : greeting}
        </p>

        <h1 className="text-4xl md:text-[42px] font-semibold tracking-tight leading-snug mb-8">
          상권과 주식,
          <br />
          <span className="text-brand">숨겨진 기회</span>를 찾아드릴게요
        </h1>

        <ChatInput onSubmit={handleSend} disabled={isLoading} />
        {isLoading && (
          <p className="mt-3 text-sm text-foreground-muted animate-pulse" role="status">
            분석 중이에요… 끝나면 워크스페이스로 이동할게요
          </p>
        )}

        <div className="mt-4 flex flex-wrap gap-2">
          {quickChips.map(({ icon: Icon, label, prompt }) => (
            <button
              key={label}
              onClick={() => handleSend(prompt)}
              disabled={isLoading}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-full border border-border bg-surface/60 text-sm text-foreground hover:bg-surface hover:border-foreground-muted/40 transition-colors disabled:opacity-50"
            >
              <Icon size={15} strokeWidth={1.75} className="text-brand" />
              {label}
            </button>
          ))}
        </div>

        <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-3">
          {workspaceCards.map(({ href, icon: Icon, title, desc }) => (
            <Link
              key={href}
              href={href}
              className="group flex items-center gap-4 bg-surface border border-border rounded-xl p-4 hover:border-brand/40 hover:shadow-sm transition-all"
            >
              <div className="w-10 h-10 grid place-items-center rounded-lg bg-brand/10 text-brand shrink-0">
                <Icon size={20} strokeWidth={1.75} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold flex items-center gap-1">
                  {title}
                  <ArrowUpRight
                    size={14}
                    className="text-foreground-muted group-hover:text-brand transition-colors"
                  />
                </div>
                <p className="text-xs text-foreground-muted mt-0.5">{desc}</p>
              </div>
            </Link>
          ))}
        </div>

        <section className="mt-12">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold flex items-center gap-2">
              <TrendingUp size={18} className="text-brand" strokeWidth={2} />
              {useRecent ? "최근 추천받은 상권" : "이런 동네는 어때요"}
            </h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {useRecent
              ? recentAreas.map((area) => (
                  <Link
                    key={area.id}
                    href={`/market?trdar=${area.trdar_code}&c=${area.conversation_id}`}
                    className="text-left bg-surface border border-border rounded-xl p-4 hover:border-brand/40 hover:shadow-sm transition-all"
                  >
                    <div className="text-base font-semibold mb-1.5 truncate">{area.trdar_name}</div>
                    <p className="text-xs text-foreground-muted mb-2">
                      {area.district_name} · {area.category}
                    </p>
                    <p className="text-xs text-foreground/80 leading-snug line-clamp-2">
                      {area.reason}
                    </p>
                  </Link>
                ))
              : defaultAreas.map((area) => (
                  <button
                    key={area.name}
                    onClick={() => handleSend(`${area.name} 상권 어때요?`)}
                    disabled={isLoading}
                    className="text-left bg-surface border border-border rounded-xl p-4 hover:border-brand/40 hover:shadow-sm transition-all disabled:opacity-50"
                  >
                    <div className="text-base font-semibold mb-1.5">{area.name}</div>
                    <p className="text-xs text-foreground-muted mb-2">{area.category}</p>
                    <p className="text-xs text-foreground/80 leading-snug">{area.note}</p>
                  </button>
                ))}
          </div>
        </section>
      </div>
    </div>
  );
}
