import { NextResponse } from "next/server";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export async function POST(request: Request) {
  try {
    const { prompt, conversationId } = await request.json();

    const res = await fetch(`${API_BASE}/chat/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, conversationId: conversationId ?? null }),
    });

    if (!res.ok) {
      const detail = await res.json().catch(() => null);
      return NextResponse.json(
        { error: detail?.detail ?? "AI 응답 오류" },
        { status: res.status },
      );
    }

    return NextResponse.json(await res.json());
  } catch (error) {
    console.error("Chat API Error:", error);
    return NextResponse.json({ error: "서버 오류가 발생했습니다." }, { status: 500 });
  }
}
