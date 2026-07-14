import type { NextConfig } from "next";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["127.0.0.1"],
  // 백엔드 GET 조회 프록시 — 엔드포인트마다 route.ts를 만들지 않는다.
  // (POST /api/chat은 에러 메시지 가공이 있어 기존 route.ts 유지)
  async rewrites() {
    return [
      {
        source: "/api/backend/:path*",
        destination: `${API_BASE}/:path*`,
      },
    ];
  },
  // 구 지도 페이지 → 상권 워크스페이스
  async redirects() {
    return [{ source: "/map", destination: "/market", permanent: false }];
  },
};

export default nextConfig;
