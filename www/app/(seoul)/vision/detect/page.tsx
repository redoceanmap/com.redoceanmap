"use client";

import { useRef, useState } from "react";
import { CloudUpload, ScanSearch, LoaderCircle, CircleAlert, UserRound } from "lucide-react";

type FaceMatch = {
  name: string;
  confidence: number;
};

type DetectResult = {
  filename: string;
  matches: FaceMatch[];
};

type DetectState = {
  dragOver: boolean;
  detecting: boolean;
  previewUrl: string | null;
  result: DetectResult | null;
  error: string | null;
};

export default function VisionDetectPage() {
  // REACT_RULES 패턴 B: dragOver·detecting·previewUrl·result·error 객체로 압축
  const [state, setState] = useState<DetectState>({
    dragOver: false,
    detecting: false,
    previewUrl: null,
    result: null,
    error: null,
  });
  const inputRef = useRef<HTMLInputElement>(null);

  const detect = async (file: File) => {
    if (!file.type.startsWith("image/")) {
      setState((prev) => ({ ...prev, dragOver: false, error: "이미지 파일만 업로드할 수 있어요." }));
      return;
    }
    const previewUrl = URL.createObjectURL(file);
    setState((prev) => {
      if (prev.previewUrl) URL.revokeObjectURL(prev.previewUrl);
      return { dragOver: false, detecting: true, previewUrl, result: null, error: null };
    });
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch("/api/vision/detect", { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "얼굴 인식에 실패했어요.");
      setState((prev) => ({ ...prev, detecting: false, result: data }));
    } catch (e) {
      setState((prev) => ({
        ...prev,
        detecting: false,
        error: e instanceof Error ? e.message : "얼굴 인식에 실패했어요.",
      }));
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) detect(file);
  };

  const best = state.result?.matches[0];

  return (
    <div className="flex-1 flex flex-col items-center px-6 pb-6">
      <div className="w-full max-w-2xl mt-12 flex flex-col gap-6">
        <div>
          <div className="flex items-center gap-2 text-brand mb-2">
            <ScanSearch size={18} strokeWidth={1.75} />
            <span className="text-sm font-medium">비전처리 · 객체탐지</span>
          </div>
          <h1 className="text-2xl font-semibold">얼굴 사진을 올려주세요</h1>
          <p className="text-sm text-foreground-muted mt-1">
            파인튜닝된 YOLO 모델이 얼굴을 탐지하고 누구인지 맞혀볼게요.
          </p>
        </div>

        <div
          role="button"
          tabIndex={0}
          onClick={() => inputRef.current?.click()}
          onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setState((prev) => (prev.dragOver ? prev : { ...prev, dragOver: true }));
          }}
          onDragLeave={() => setState((prev) => ({ ...prev, dragOver: false }))}
          onDrop={handleDrop}
          className={`flex flex-col items-center justify-center gap-3 min-h-[260px] rounded-2xl border-2 border-dashed cursor-pointer transition-colors ${
            state.dragOver
              ? "border-brand bg-brand/5"
              : "border-border bg-surface hover:border-foreground-muted/40"
          }`}
        >
          {state.detecting ? (
            <>
              <LoaderCircle size={28} strokeWidth={1.75} className="text-brand animate-spin" />
              <p className="text-sm text-foreground-muted">얼굴을 찾는 중...</p>
            </>
          ) : (
            <>
              <CloudUpload size={28} strokeWidth={1.75} className="text-brand" />
              <p className="text-sm text-foreground/80">
                얼굴 사진을 여기에 끌어다 놓거나 <span className="text-brand font-medium">클릭해서 선택</span>
              </p>
              <p className="text-xs text-foreground-muted">PNG · JPG · WEBP 등 이미지 파일</p>
            </>
          )}
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) detect(file);
              e.target.value = "";
            }}
          />
        </div>

        {state.error && (
          <div className="flex items-center gap-2 px-4 py-3 rounded-xl border border-brand/30 bg-brand/5 text-sm text-brand">
            <CircleAlert size={16} strokeWidth={1.75} />
            {state.error}
          </div>
        )}

        {state.result && (
          <div className="flex flex-col sm:flex-row gap-4 p-5 rounded-2xl border border-border bg-surface">
            {state.previewUrl && (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={state.previewUrl}
                alt={state.result.filename}
                className="w-full sm:w-40 h-40 object-cover rounded-xl border border-border"
              />
            )}
            <div className="flex flex-col gap-1.5 min-w-0">
              {best ? (
                <>
                  <div className="flex items-center gap-1.5 text-sm font-medium text-brand">
                    <UserRound size={16} strokeWidth={2} />
                    이 사람은...
                  </div>
                  <p className="text-2xl font-semibold">{best.name}</p>
                  <p className="text-xs text-foreground-muted">
                    신뢰도 {(best.confidence * 100).toFixed(1)}%
                  </p>
                  {state.result.matches.length > 1 && (
                    <p className="text-xs text-foreground-muted mt-1">
                      그 외 후보:{" "}
                      {state.result.matches
                        .slice(1)
                        .map((m) => `${m.name} (${(m.confidence * 100).toFixed(0)}%)`)
                        .join(", ")}
                    </p>
                  )}
                </>
              ) : (
                <>
                  <div className="flex items-center gap-1.5 text-sm font-medium">
                    <CircleAlert size={16} strokeWidth={2} className="text-brand" />
                    얼굴을 찾지 못했어요
                  </div>
                  <p className="text-sm text-foreground-muted">
                    얼굴이 또렷하게 나온 사진으로 다시 시도해 주세요.
                  </p>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
