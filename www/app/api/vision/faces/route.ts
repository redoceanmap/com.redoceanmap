import { NextResponse } from "next/server";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const cookie = request.headers.get("cookie");

    const res = await fetch(`${API_BASE}/vision/faces`, {
      method: "POST",
      headers: cookie ? { Cookie: cookie } : undefined,
      body: formData,
    });

    if (!res.ok) {
      const detail = await res.json().catch(() => null);
      return NextResponse.json(
        { error: detail?.detail ?? "얼굴 인식 오류" },
        { status: res.status },
      );
    }

    return NextResponse.json(await res.json());
  } catch (error) {
    console.error("Vision Faces API Error:", error);
    return NextResponse.json({ error: "서버 오류가 발생했습니다." }, { status: 500 });
  }
}
