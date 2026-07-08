const toggles = [
  { group: "추천 엔진", items: [
    { label: "실시간 추천 활성화", desc: "AI 상권 추천 API를 운영 환경에 노출", on: true },
    { label: "공공데이터 실계산 우선", desc: "추정치보다 실측 데이터를 우선 사용", on: true },
    { label: "베타 모델 사용", desc: "gemini-3.1-flash-lite 실험 버전", on: false },
  ]},
  { group: "알림", items: [
    { label: "동기화 실패 알림", desc: "파이프라인 오류 시 이메일 발송", on: true },
    { label: "주간 리포트", desc: "매주 월요일 운영 요약 발송", on: true },
    { label: "신규 가입 알림", desc: "회원 가입 시 슬랙 알림", on: false },
  ]},
];

export default function SettingsPage() {
  return (
    <div className="max-w-3xl mx-auto space-y-5">
      <div>
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight">설정</h1>
        <p className="mt-1 text-sm text-foreground-muted">서비스 운영 환경 구성</p>
      </div>

      {/* 일반 */}
      <section className="rounded-2xl bg-surface border border-border p-5 space-y-4">
        <h2 className="font-semibold">일반</h2>
        <Field label="서비스 이름" defaultValue="redoceanmap" />
        <Field label="관리자 이메일" defaultValue="jang971121@gmail.com" type="email" />
        <div>
          <label className="text-sm font-medium">기본 지역</label>
          <select
            name="region"
            defaultValue="서울특별시"
            className="mt-1.5 w-full h-11 px-3.5 rounded-xl bg-background border border-border text-sm outline-none focus:border-brand"
          >
            <option>서울특별시</option>
            <option>경기도</option>
            <option>인천광역시</option>
          </select>
        </div>
      </section>

      {/* 토글 그룹 */}
      {toggles.map((g) => (
        <section key={g.group} className="rounded-2xl bg-surface border border-border p-5">
          <h2 className="font-semibold">{g.group}</h2>
          <div className="mt-2 divide-y divide-border">
            {g.items.map((t) => (
              <div key={t.label} className="flex items-center justify-between gap-4 py-3.5">
                <div className="min-w-0">
                  <p className="text-sm font-medium">{t.label}</p>
                  <p className="text-xs text-foreground-muted mt-0.5">{t.desc}</p>
                </div>
                <Toggle defaultOn={t.on} />
              </div>
            ))}
          </div>
        </section>
      ))}

      <div className="flex justify-end gap-2 pb-2">
        <button type="button" className="px-4 h-10 rounded-full border border-border text-sm font-medium hover:bg-black/5 transition-colors">
          취소
        </button>
        <button type="button" className="px-5 h-10 rounded-full bg-brand text-white text-sm font-medium hover:bg-brand-deep transition-colors">
          변경사항 저장
        </button>
      </div>
    </div>
  );
}

function Field({ label, defaultValue, type = "text" }: { label: string; defaultValue: string; type?: string }) {
  return (
    <div>
      <label className="text-sm font-medium">{label}</label>
      <input
        name={label}
        type={type}
        defaultValue={defaultValue}
        className="mt-1.5 w-full h-11 px-3.5 rounded-xl bg-background border border-border text-sm outline-none focus:border-brand"
      />
    </div>
  );
}

// CSS peer 기반 무상태 토글
function Toggle({ defaultOn }: { defaultOn: boolean }) {
  return (
    <label className="relative inline-flex items-center cursor-pointer shrink-0">
      <input type="checkbox" defaultChecked={defaultOn} className="sr-only peer" />
      <span className="w-11 h-6 rounded-full bg-border peer-checked:bg-brand transition-colors" />
      <span className="absolute left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform peer-checked:translate-x-5" />
    </label>
  );
}
