import { ChevronDown, Sparkles } from "lucide-react";

// 이 종목을 설명한 마지막 챗 답변을 스테이지에 고정한다 — 채팅 패널에만 두면
// 스크롤·종목 전환에 묻혀 "왜 이 판정인가"를 다시 찾아야 한다. 기본은 한 줄로 접어 둔다.
export default function SymbolSummary({ text }: { text: string }) {
  return (
    <details className="shrink-0 group px-4 py-2 border-b border-border">
      <summary className="flex items-start gap-1.5 cursor-pointer list-none select-none text-xs">
        <Sparkles size={13} className="mt-0.5 shrink-0 text-brand" />
        <span className="flex-1 line-clamp-1 text-foreground-muted group-open:hidden">{text}</span>
        <span className="hidden group-open:block flex-1 font-medium">이 종목 요약</span>
        <ChevronDown
          size={13}
          className="mt-0.5 shrink-0 text-foreground-muted transition-transform group-open:rotate-180"
        />
      </summary>
      <p className="mt-1.5 pl-[18px] pr-4 text-xs leading-relaxed whitespace-pre-wrap">{text}</p>
    </details>
  );
}
