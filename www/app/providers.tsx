"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export default function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60_000, // 심볼/상권 전환 시 캐시 히트가 UX 핵심
            retry: (failureCount, error) => {
              // 404(수집 대상 아님)·401/403(인증·권한)은 재시도해도 결과가 같다 —
              // 비로그인 상태에서 yfinance를 태우는 analyze가 3번씩 나가던 낭비를 막는다
              const status =
                error instanceof Error && "status" in error
                  ? (error as Error & { status?: number }).status
                  : undefined;
              return status !== 404 && status !== 401 && status !== 403 && failureCount < 2;
            },
          },
        },
      }),
  );
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
