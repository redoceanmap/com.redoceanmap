"use client";

import {
  Store,
  Wallet,
  MapPin,
  BarChart3,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import { useChatStore } from "@/lib/store";
import { useUIStore } from "@/lib/uiStore";
import ChatInput from "@/components/seoul/ChatInput";
import ChatView from "@/components/seoul/ChatView";

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

const trendingAreas = [
  { name: "성수동", category: "카페·디저트", change: "+12%", note: "젊은 손님이 늘고 있어요" },
  { name: "연남동", category: "베이커리", change: "+8%", note: "주말 매출이 강해요" },
  { name: "망원동", category: "외식업", change: "+6%", note: "객단가가 올라가요" },
  { name: "익선동", category: "야간 상권", change: "+5%", note: "밤에 사람이 모여요" },
];

export default function HomePage() {
  const messages = useChatStore((s) => s.messages);
  const isLoading = useChatStore((s) => s.isLoading);
  const sendMessage = useChatStore((s) => s.sendMessage);
  const user = useUIStore((s) => s.user);
  const hasChat = messages.length > 0;

  const handleSend = (text: string) => {
    void sendMessage(text);
  };

  if (hasChat) {
    return (
      <div className="flex-1 flex flex-col min-h-0">
        <div className="flex-1 overflow-y-auto px-6">
          <ChatView />
        </div>
        <div className="px-6 pb-6 pt-2">
          <div className="max-w-3xl mx-auto">
            <ChatInput onSubmit={handleSend} disabled={isLoading} />
          </div>
        </div>
      </div>
    );
  }

  const hour = new Date().getHours();
  const greeting = getGreeting(hour);

  return (
    <div className="flex-1 flex justify-center items-center px-6 py-12">
      <div className="w-full max-w-3xl flex flex-col">
        <p className="text-sm text-foreground-muted mb-3">
          {user ? `${greeting}, ${user.name}님` : greeting}
        </p>

        <h1 className="text-4xl md:text-[42px] font-semibold tracking-tight leading-snug mb-8">
          서울 상권,
          <br />
          <span className="text-brand">숨겨진 기회</span>를 찾아드릴게요
        </h1>

        <ChatInput onSubmit={handleSend} disabled={isLoading} />

        <div className="mt-4 flex flex-wrap gap-2">
          {quickChips.map(({ icon: Icon, label, prompt }) => (
            <button
              key={label}
              onClick={() => handleSend(prompt)}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-full border border-border bg-surface/60 text-sm text-foreground hover:bg-surface hover:border-foreground-muted/40 transition-colors"
            >
              <Icon size={15} strokeWidth={1.75} className="text-brand" />
              {label}
            </button>
          ))}
        </div>

        <section className="mt-14">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold flex items-center gap-2">
              <TrendingUp size={18} className="text-brand" strokeWidth={2} />
              지금 뜨는 동네
            </h2>
            <button className="text-sm text-foreground-muted hover:text-foreground">
              전체 보기
            </button>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {trendingAreas.map((area) => (
              <button
                key={area.name}
                onClick={() => handleSend(`${area.name} 상권 어때요?`)}
                className="text-left bg-surface border border-border rounded-xl p-4 hover:border-brand/40 hover:shadow-sm transition-all"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-base font-semibold">{area.name}</span>
                  <span className="text-xs font-semibold text-brand">
                    {area.change}
                  </span>
                </div>
                <p className="text-xs text-foreground-muted mb-2">
                  {area.category}
                </p>
                <p className="text-xs text-foreground/80 leading-snug">
                  {area.note}
                </p>
              </button>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
