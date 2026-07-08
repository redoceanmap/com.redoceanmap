# redoceanmap 프론트엔드 계획

## 1. 개요

서울시 상권 분석 서비스 `redocean-seoul`의 프론트엔드. 사용자가 "3000만원으로 카페 차리고 싶어" 같은 자연어 프롬프트를 입력하면, AI가 추천 상권과 분석 결과를 자연어로 응답하고 지도에서 위치를 보여주는 서비스.

- 메인 페이지: Claude.ai 스타일의 대화형 UI
- 지도 페이지: 대화에서 추천된 상권을 마커로 시각화

백엔드 PLAN: `../backend/PLAN.md`

---

## 2. 사용자 시나리오

```
[사용자]  "3000만원으로 카페 차리고 싶은데 어디가 좋을까?"
   ↓
[AI 응답] "괜찮아 보이는 동네 3곳 골라봤어요. 지도에서 볼래요?"
   ↓ ("지도에서 볼래요?" 클릭)
[지도]   서울 지도에 추천 동네 3곳 마커 표시
   ↓ (마커 클릭)
[패널]   매출, 폐업률, 유동인구 상세
```

---

## 3. 기술 스택 (확정)

| 영역 | 선택 | 이유 |
|---|---|---|
| 프레임워크 | **Next.js** (App Router) | Vercel 배포, 카카오맵 SDK 호환 |
| 스타일링 | **Tailwind CSS** | 빠른 시안, 컬러 시스템 일관성 |
| 상태 관리 | **Zustand** | 대화 ↔ 지도 페이지 간 추천 결과 공유, 가벼움 |
| 지도 | **Kakao Map JS SDK** | 한국 행정구/동 데이터 매칭, 무료 |
| 폰트 | **Pretendard** | 한국어 가독성 표준 |
| 아이콘 | **Lucide React** | 깔끔, 일관적 |

---

## 4. 폴더 구조

```
frontend/
├── package.json
├── next.config.ts
├── tailwind.config.ts
├── .env.local              # NEXT_PUBLIC_KAKAO_MAP_KEY
├── app/
│   ├── layout.tsx          # 공통 사이드바 + 전체 레이아웃
│   ├── page.tsx            # / → (seoul)로 리다이렉트
│   └── (seoul)/
│       ├── page.tsx        # 대화형 메인
│       └── map/page.tsx    # 지도 페이지
├── components/
│   ├── seoul/              # Sidebar, ChatInput, ChatMessage,
│   │                       # QuickStartChips, MapView, RecommendPanel
│   └── shared/             # Button 등 공용
├── lib/
│   ├── store.ts            # Zustand store (추천 결과)
│   └── mockApi.ts          # MVP용 더미 응답
└── public/
```

모듈러 방침: 단일 Next.js, `app/(seoul)/` 라우트 그룹으로 모듈 분리. 향후 `(doro)`, `(agora)` 등 연습 앱 추가 가능.

---

## 5. 디자인 시스템

### 컬러 (버건디 + 미니멀)

```
브랜드 레드     #722F37  (버건디/와인)   ← 메인 강조, 로고, 버튼
딥 액센트       #4A1D24  (호버, 진한 강조)
오프화이트 배경  #FAF7F2  (이미지 톤 유지)
텍스트 다크      #1A1A1A
보조 텍스트      #6B6B6B
보더/구분선      #E8E2D9
```

→ 채도 낮은 와인 컬러로 "고급 부동산" 느낌. 빨강은 강조에만 쓰고 면적은 작게.

### 폰트
- **Pretendard** (한국어 표준)
- 제목 700, 본문 400~500, 산세리프 통일

### 시그니처 마크
- **빨간 핀 📍** — redoceanmap 로고 시그니처
- Claude.ai의 `✻` 자리 = 우리는 빨간 핀

### 사이드바 메뉴 (Lucide 아이콘 + 토스어 라벨)

| 아이콘 | 라벨 |
|---|---|
| `Plus` | 새로 물어보기 |
| `Search` | 지난 대화 찾기 |
| `MessageSquare` | 지난 대화 |
| `MapPin` | 지도로 보기 |
| `Bookmark` | 찜한 동네 |
| `User` | 내 정보 |

---

## 6. 토스어 카피 가이드

원칙: 쉬운 말 / 짧고 직관적 / 친근한 어체 / 전문용어 풀어쓰기 / 긍정적 표현.

### 인사말 (시간대별)
- 오전: "좋은 아침이에요, 장민석님"
- 오후: "오후예요, 장민석님"
- 저녁: "오늘 하루 어땠어요?"

### 서브카피 (인사말 아래)
> "오늘은 어디 들여다볼까요?"

### 입력창 플레이스홀더
> "예산이랑 하고 싶은 업종을 알려주세요"

### 빠른 시작 칩 (메인 페이지)

| 아이콘 | 라벨 |
|---|---|
| `Store` | 업종으로 찾기 |
| `Wallet` | 예산으로 찾기 |
| `MapPin` | 동네로 찾기 |
| `BarChart3` | 상권 비교 |
| `Sparkles` | 추천받기 |

### 응답 톤 (백엔드 연동 시 참고)

| ❌ 딱딱한 표현 | ✅ 토스어 표현 |
|---|---|
| "해당 지역은 카페 업종의 공급 과잉 상태입니다." | "이 동네는 카페가 좀 많아요. 비슷한 가게가 [N]개나 있거든요." |
| "추정 매출 분석 결과를 제공합니다." | "이 자리에서 한 달에 얼마 벌 수 있을지 봤어요." |
| "조회된 결과가 없습니다." | "음, 조건에 맞는 동네를 못 찾았어요. 예산을 좀 늘려볼까요?" |
| "추천 상권 Top 3을 시각화합니다." | "괜찮아 보이는 동네 3곳 골라봤어요. 지도에서 볼래요?" |

### 버튼 라벨
- "지도에서 볼래요?" (응답 안의 CTA)
- "더 자세히"
- "비슷한 곳 더 보기"
- "다시 물어보기"

---

## 7. 구현 순서 (검증 기준 포함)

8단계, 3개 묶음으로 나눠 검증 단위로 진행.

### 묶음 A — 정적 UI

| Step | 작업 | 검증 |
|---|---|---|
| 1 | `create-next-app` + Tailwind + Zustand + Lucide 셋업, Pretendard 로드 | `npm run dev` → localhost:3000 뜸 |
| 2 | `app/layout.tsx`에 좌측 사이드바 (정적) | 모든 페이지에서 사이드바 보임 |
| 3 | `(seoul)/page.tsx`: 인사말 + 입력창 + 빠른 시작 칩 | 첨부 이미지 톤과 시각적으로 일치 |

### 묶음 B — 대화 동작

| Step | 작업 | 검증 |
|---|---|---|
| 4 | 입력 → `mockApi.ts`로 더미 응답 → 메시지 스트림 렌더링 | 입력 시 메시지 추가, 응답에 "지도에서 볼래요?" 버튼 |
| 5 | Zustand store에 추천 좌표 저장 | 응답 직후 store에 마커 좌표 들어감 |

### 묶음 C — 지도 페이지 ⚠️ 카카오맵 JS 키 필요

| Step | 작업 | 검증 |
|---|---|---|
| 6 | Kakao Map SDK 연동 + `(seoul)/map/page.tsx`에 더미 마커 3개 | 서울 지도 + 마커 표시 |
| 7 | "지도에서 볼래요?" 클릭 → `/map` 라우팅 + store 좌표 마커 렌더 | 대화 → 지도, 좌표 일치 |
| 8 | 마커 클릭 → 우측 상세 패널 (매출/폐업률/유동인구, 더미) | 패널 열림 |

---

## 8. 가정 및 범위 외

### 가정
- 백엔드 연동은 별도 단계. MVP 8단계는 `mockApi.ts`로 화면 완결성만 검증.
- 카카오맵 JS 키는 사용자가 [Kakao Developers](https://developers.kakao.com)에서 발급해 `.env.local`의 `NEXT_PUBLIC_KAKAO_MAP_KEY`에 넣음.
- 디자인은 첨부 이미지 톤(오프화이트, 미니멀, 산세리프) 유지.

### 범위 외 (MVP 이후)
- 다국어, 다크모드, 인증
- LLM 응답 스트리밍 (백엔드 연동 시)
- 사이드바 "대화 기록"의 영속화 (localStorage / DB)
- 모바일 반응형 깊이 (데스크탑 먼저)

---

## 9. 시작 명령어

```bash
cd /Users/jangminseok/project/com.redoceanmap/frontend

# Step 1: 셋업 (묶음 A 시작 시 1회만)
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"
npm install zustand lucide-react
npm install --save-dev @types/node

# Pretendard 로드는 app/layout.tsx에서 next/font 또는 CDN

# 개발 서버
npm run dev

# Step 6 진입 전: .env.local 만들기
echo "NEXT_PUBLIC_KAKAO_MAP_KEY=발급받은_JS_키" > .env.local
```

---

## 10. 다음 세션 시작 방법

새 대화에서 진행할 때:

```
"frontend/PLAN.md 보고 묶음 A 시작해줘"
```

또는

```
"frontend/PLAN.md의 Step 1부터 진행"
```

이 문서 + `backend/PLAN.md` + 첨부 이미지 톤 정도면 컨텍스트 충분.
