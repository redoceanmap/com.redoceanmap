"use client";

import { useRef, useState } from "react";
import { CloudUpload, ScanEye, LoaderCircle, CircleAlert, CircleCheck } from "lucide-react";

type VisionResult = {
  filename: string;
  contentType: string;
  sizeBytes: number;
  message: string;
};

type UploadState = {
  dragOver: boolean;
  uploading: boolean;
  previewUrl: string | null;
  result: VisionResult | null;
  error: string | null;
};

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function VisionPage() {
  // REACT_RULES 패턴 B: dragOver·uploading·previewUrl·result·error 객체로 압축
  const [state, setState] = useState<UploadState>({
    dragOver: false,
    uploading: false,
    previewUrl: null,
    result: null,
    error: null,
  });
  const inputRef = useRef<HTMLInputElement>(null);

  const upload = async (file: File) => {
    if (!file.type.startsWith("image/")) {
      setState((prev) => ({ ...prev, dragOver: false, error: "이미지 파일만 업로드할 수 있어요." }));
      return;
    }
    const previewUrl = URL.createObjectURL(file);
    setState((prev) => {
      if (prev.previewUrl) URL.revokeObjectURL(prev.previewUrl);
      return { dragOver: false, uploading: true, previewUrl, result: null, error: null };
    });
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch("/api/vision", { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "업로드에 실패했어요.");
      setState((prev) => ({ ...prev, uploading: false, result: data }));
    } catch (e) {
      setState((prev) => ({
        ...prev,
        uploading: false,
        error: e instanceof Error ? e.message : "업로드에 실패했어요.",
      }));
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) upload(file);
  };

  return (
    <div className="flex-1 flex flex-col items-center px-6 pb-6">
      <div className="w-full max-w-2xl mt-12 flex flex-col gap-6">
        <div>
          <div className="flex items-center gap-2 text-brand mb-2">
            <ScanEye size={18} strokeWidth={1.75} />
            <span className="text-sm font-medium">비전처리</span>
          </div>
          <h1 className="text-2xl font-semibold">이미지를 올려주세요</h1>
          <p className="text-sm text-foreground-muted mt-1">
            드래그 앤 드랍 또는 클릭으로 업로드하면 비전 처리 서버로 전송돼요.
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
          {state.uploading ? (
            <>
              <LoaderCircle size={28} strokeWidth={1.75} className="text-brand animate-spin" />
              <p className="text-sm text-foreground-muted">업로드 중...</p>
            </>
          ) : (
            <>
              <CloudUpload size={28} strokeWidth={1.75} className="text-brand" />
              <p className="text-sm text-foreground/80">
                이미지를 여기에 끌어다 놓거나 <span className="text-brand font-medium">클릭해서 선택</span>
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
              if (file) upload(file);
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
              <div className="flex items-center gap-1.5 text-sm font-medium">
                <CircleCheck size={16} strokeWidth={2} className="text-brand" />
                업로드 완료
              </div>
              <p className="text-sm truncate">{state.result.filename}</p>
              <p className="text-xs text-foreground-muted">
                {state.result.contentType} · {formatBytes(state.result.sizeBytes)}
              </p>
              <p className="text-sm text-foreground/80 mt-1">{state.result.message}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
