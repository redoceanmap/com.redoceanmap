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
            retry: (failureCount, error) =>
              // 404(수집 대상 아님)는 재시도 무의미
              !(error instanceof Error && "status" in error && error.status === 404) &&
              failureCount < 2,
          },
        },
      }),
  );
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
