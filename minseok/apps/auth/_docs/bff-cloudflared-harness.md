# BFF-CLOUDFLARED-HARNESS

Claude Code 작업 지시서 — ① cloudflared 도커 전환 + 포트 잠금, ② OAuth 패턴 A(BFF, httpOnly 쿠키) 전환
대상 저장소: com.redoceanmap 모노레포 (`minseok/` FastAPI + `www/` Next.js), 실행 환경: 백엔드 PC(window 브랜치)
선행 문서: `auth-gateway-harness-redoceanmap.md`(완료됨 — RS256·auth 컨테이너 분리·프록시 분기)

**핵심 원칙: 서버로 들어오는 길은 Cloudflare 터널 하나로 좁히고, 토큰은 브라우저 JS가 만질 수 없는 곳(httpOnly 쿠키)에만 둔다.**

> ⚠️ 이 문서는 이전 지시서의 절대 규칙 6 "쿠키를 발급하지 않는다"를 **공식 폐기**한다.
> 쿠키 전환 보류(2026-07-21)는 2026-07-22 사용자 결정으로 해제되었다. 나머지 규칙은 전부 유효하다.

---

## 0. 컨텍스트 — 현재 상태 (2026-07-22, mac 브랜치 c983fd7 기준)

- backend(8000)·auth(9000) 컨테이너 분리 완료, JWT RS256(발급=auth 개인키, 검증=공개키) 완료.
- cloudflared는 **백엔드 PC 호스트 프로세스**(로컬 관리형 터널 `redoceanmap`), 서비스들은 `"8000:8000"` 형식(0.0.0.0)으로 호스트에 공개 — **같은 LAN의 모든 기기가 DB(5432)·redis(6379)·neo4j까지 직접 접속 가능한 상태다.**
- 소셜 로그인은 패턴 B: 프론트가 `window.location.origin + /oauth/{provider}`로 코드를 받아
  (`www/lib/socialAuth.ts`, `www/app/oauth/[provider]/`), `/api/backend/auth/social`로 POST → auth 컨테이너가 토큰 교환.
- 토큰은 **localStorage**(`www/lib/tokenStorage.ts`) — XSS 시 탈취 가능. 이걸 없애는 것이 Part B의 목적.
- 프론트 route 핸들러(`www/app/api/chat/route.ts`, `vision*`)가 Authorization 헤더를 백엔드로 중계.
- 네이버·카카오 콘솔 콜백 등록: `https://redoceanmap.com/oauth/{p}`, `https://www.redoceanmap.com/oauth/{p}`, `http://localhost:3000/oauth/{p}`.

## 1. 절대 규칙 (위반 시 작업 중단 후 보고)

1. 이전 지시서 규칙 승계: 헥사고날·스타 토폴로지·`.importlinter` 계약 준수, RS256 리터럴 하드코딩 유지,
   개인키 참조는 발급 코드에만, 키·secret 커밋 금지, roles를 JWT 클레임에 넣지 않음(매 요청 DB 조회 유지).
2. **쿠키 스펙 고정:** `HttpOnly` + `SameSite=Lax` + `Secure`(prod) + `Path=/`. `Secure`는 ENV로 분기(개발 http 허용), 나머지는 리터럴. 토큰을 응답 본문으로 반환하는 코드는 전환 완료 시점에 0건이어야 한다.
3. **access token을 localStorage/sessionStorage에 저장하는 코드를 남기지 않는다** — `tokenStorage.ts`는 삭제 대상.
4. 포트 잠금 후 `docker-compose.yaml`에 `0.0.0.0` 바인딩(`"포트:포트"` 축약형 포함)이 한 줄도 없어야 한다.
5. 전환 순서 준수: 각 단계에서 서비스 전체가 동작해야 한다. 특히 Part A의 무중단 절차(커넥터 병행)와
   Part B의 콘솔 콜백 선등록(§6)을 지키지 않으면 로그인·외부 접속이 끊긴다.
6. 불명확한 지점은 추측하지 말고 질문한다. 특히 cloudflared config의 실제 ingress 목록과 www(3000)의 실행 방식(호스트 프로세스 여부)은 **읽고 확인한 뒤** 진행한다.

---

## Part A — cloudflared 도커 전환 + 포트 잠금

### A.1 사전 조사 (수정 전 보고)

- 백엔드 PC의 cloudflared config(`%USERPROFILE%\.cloudflared\config.yml` 상당)와 credentials JSON 위치·내용(ingress 전체 목록)을 읽고 요약한다.
- www(Next.js, 3000)가 호스트 프로세스인지 컨테이너인지 확인한다.
- 호스트 cloudflared가 Windows 서비스인지(`cloudflared service install`로 설치됐는지) 확인한다.

### A.2 compose에 cloudflared 서비스 추가

```yaml
  cloudflared:
    image: cloudflare/cloudflared:latest
    restart: unless-stopped
    command: tunnel --config /etc/cloudflared/config.yml run
    volumes:
      - <호스트 .cloudflared 디렉토리>:/etc/cloudflared:ro
    depends_on:
      - backend
      - auth
```

- 마운트용으로 **복사본 디렉토리를 만들지 말고** 기존 `.cloudflared`를 read-only 마운트한다. 단, config 안의
  `credentials-file:` 경로는 컨테이너 기준(`/etc/cloudflared/<tunnel-id>.json`)으로 고쳐야 한다 —
  호스트 cloudflared와 병행 기동해야 하므로, 컨테이너 전용 config 사본(`config-docker.yml`)을 같은 디렉토리에 두고
  `--config /etc/cloudflared/config-docker.yml`로 지정하는 방식을 권장한다(원본 config는 롤백용으로 무수정 보존).
- `config-docker.yml`의 ingress 주소 변환:
  - compose 서비스 → 서비스명: `http://backend:8000`, `http://auth:9000`, `http://n8n:5678`
  - 호스트 프로세스(www 등) → `http://host.docker.internal:3000`
  - Docker Desktop(Windows)은 `host.docker.internal`이 127.0.0.1 바인딩 서비스에도 닿는다. A.4에서 실측 검증한다.

### A.3 무중단 전환

1. `docker compose up -d cloudflared` — 호스트 cloudflared는 **아직 끄지 않는다** (터널은 다중 커넥터 허용).
2. Cloudflare 대시보드에서 터널 커넥터가 2개(호스트+컨테이너) 연결됐는지 확인.
3. 외부에서 전 호스트네임 응답 확인 (`https://redoceanmap.com`, `api.`, `auth.`, `n8n.` 등 config에 있는 전부).
4. 호스트 cloudflared 중지·서비스 제거(`cloudflared service uninstall`). 커넥터 1개(컨테이너)만 남은 상태에서 3번 재확인.
5. 문제 발생 시 롤백: 호스트 서비스 재기동이 곧 롤백이다 — 원본 config를 남겨둔 이유.

### A.4 포트 잠금 (A.3 검증 후 별도 커밋)

`docker-compose.yaml`의 모든 `ports:`를 루프백 바인딩으로 교체한다:

| 서비스 | 변경 | 근거 |
|---|---|---|
| backend | `"127.0.0.1:8000:8000"` | www(호스트 프로세스) rewrites가 사용 |
| auth | `"127.0.0.1:9000:9000"` | 동일 |
| n8n | `"127.0.0.1:5678:5678"` | 터널은 도커 네트워크 경유, 로컬 UI 접근용만 유지 |
| pgvector | `"127.0.0.1:5432:5432"` | 맥의 SSH 포트포워딩은 호스트 루프백을 타므로 영향 없음 |
| redis / neo4j | `"127.0.0.1:..."` | 컨테이너 간에는 도커 네트워크로 통신 — 호스트 포트는 로컬 도구용만 |

- 잠금 후 검증: 같은 LAN의 다른 기기(맥)에서 `nc -vz <백엔드PC IP> 5432` 등이 **실패**해야 하고,
  외부에서 `https://redoceanmap.com` 등 전 호스트네임은 정상이어야 한다.

---

## Part B — OAuth 패턴 A(BFF) 전환

### B.0 설계 결정 (이대로 구현)

콜백을 `auth.redoceanmap.com`이 아니라 **프론트 origin의 프록시 경로**로 받는다:

```
[시작]  브라우저 → GET /api/backend/auth/social/{provider}/start?return_to=/market
        (rewrites가 auth:9000으로 프록시) → auth가 state 생성·state 쿠키 설정 → 302 네이버/카카오/구글 인가 페이지
[콜백]  프로바이더 → 브라우저 → GET https://redoceanmap.com/api/backend/auth/social/{provider}/callback?code&state
        → auth가 state 쿠키 검증 → 코드 교환(기존 인터랙터 재사용) → JWT 발급
        → Set-Cookie(access·refresh, httpOnly) → 302 return_to(프론트 페이지)
```

근거: 쿠키가 처음부터 프론트 origin의 퍼스트파티라 서브도메인 쿠키/CORS 문제가 없고, dev(`localhost:3000` → 127.0.0.1:9000 프록시)와 prod가 완전 대칭이며, 프록시 분기(`/api/backend/auth/*` → 9000)를 그대로 활용한다.
`auth.redoceanmap.com`은 콜백에 쓰지 않는다(서버 간·비브라우저 용도로만 유지).

- redirect_uri는 서버가 env `AUTH_PUBLIC_BASE_URL`(prod `https://redoceanmap.com`, dev `http://localhost:3000`)로 조립한다. 프론트가 redirect_uri를 만들어 보내는 코드는 제거된다.
- state는 서버 생성 → 단기(10분) httpOnly 쿠키 + 콜백 쿼리 비교. 기존 프론트 sessionStorage state 로직은 삭제.
- `www.redoceanmap.com` 유입은 쿠키가 apex에 묶이므로, Cloudflare 리다이렉트 룰로 www→apex 표준화한다(§6). 코드에서 Domain 속성으로 풀지 않는다(단순성 우선).

### B.1 auth 앱 — start/callback 엔드포인트

- `social_router`에 `GET /auth/social/{provider}/start`, `GET /auth/social/{provider}/callback` 추가.
- 인가 URL 조립(클라이언트 ID·authorize URL·scope·prompt 파라미터)은 현재 `www/lib/socialAuth.ts`에 있는 값을 서버로 이식한다. `KAKAO_CLIENT_ID` 등은 이미 `.env.auth`에 있다(§0의 이전 지시서 §5.3 완료 전제 — 없으면 질문).
- 코드 교환·가입/로그인·동의 흐름은 **기존 `social_interactor`·`social_oauth_gateway`를 그대로 재사용**한다. 신규 로직은 어댑터 계층(라우터)의 state 쿠키·리다이렉트 처리로 한정한다. 슬라이스 1:1 컨벤션상 새 슬라이스를 만들지 않는다 — 기존 social 슬라이스의 확장이다.
- 동의(consent)가 필요한 신규 소셜 가입: 콜백에서 동의 토큰을 발급받으면 쿠키를 심지 말고 `return_to` 대신 프론트 동의 페이지로 302 하되, 동의 토큰 전달 방식은 기존 프론트 동의 UI 구조를 읽고 결정한다(불명확하면 질문).

### B.2 쿠키 발급/해제 — 일반 로그인 포함 전면 전환

- 로그인·가입·소셜 콜백·리프레시 응답에서 access/refresh 토큰을 **Set-Cookie로 내리고 본문에서 제거**한다.
  쿠키명 `access_token`·`refresh_token`, 속성은 규칙 2. 만료는 기존 수명(60분/14일)과 일치시킨다.
- `POST /auth/logout` 신규 — 두 쿠키 삭제(+ 기존 리프레시 폐기 로직이 있으면 호출).
- 쿠키 조립은 한 곳(예: `apps/auth/adapter/inbound/api/cookie.py` 헬퍼)으로 모은다 — 라우터마다 속성 나열 금지.

### B.3 검증부 — 쿠키 우선, 헤더 fallback

- `core/security.py get_current_user_id`: `access_token` 쿠키 우선, 없으면 기존 `Authorization: Bearer` fallback 유지(테스트·도구·향후 비브라우저 클라이언트용). `/auth/tabs`·`get_me` 등 auth 내부 검증 경로도 동일.
- 매 요청 계정 상태 검사(정지/탈퇴 즉시 차단)는 그대로.

### B.4 프론트 정리

- 삭제: `www/lib/tokenStorage.ts`, `www/app/oauth/[provider]/`(콜백 페이지), `socialAuth.ts`의 state/redirect_uri/클라이언트 ID 로직, `NEXT_PUBLIC_*_CLIENT_ID` 참조 전부.
- `startSocialLogin(provider)`는 `window.location.href = "/api/backend/auth/social/{provider}/start?return_to=" + encodeURIComponent(현재경로)` 한 줄로 축소.
- `authApi.ts`: Authorization 헤더 제거. 같은 origin 프록시 호출이므로 fetch 기본값으로 쿠키가 동행한다. 로그인 상태 판정은 토큰 존재 여부 대신 `GET /auth/me` 성공 여부로.
- 리프레시: 401 수신 시 `/api/backend/auth/refresh` 호출(쿠키 기반) 후 원 요청 재시도 — 기존 리프레시 흐름을 쿠키 기반으로만 바꾸고 구조는 유지.
- `www/app/api/*` route 핸들러(chat·vision 등): Authorization 중계를 **Cookie 헤더 중계**로 교체(백엔드 검증부가 쿠키를 읽으므로).

### B.5 테스트

- 기존 보안 테스트(`test_security_guard.py` 등)는 헤더 fallback으로 무수정 통과해야 한다.
- 신규: 쿠키로 보호 엔드포인트 통과 / 쿠키 위조 401 / state 불일치 콜백 거부 / 콜백 성공 시 Set-Cookie 속성(HttpOnly·SameSite=Lax) 검증 / logout 후 쿠키 삭제 확인.
- 프론트: 로그인 → 새로고침 후 세션 유지 → 로그아웃 수동 시나리오를 완료 보고에 포함.

---

## 2. 범위 밖 — 하지 않는다

| 항목 | 사유 |
|---|---|
| PKCE | confidential client(서버가 secret 보유)로 충분. 네이버는 PKCE 미지원 |
| CSRF 토큰(double-submit) | SameSite=Lax가 기준선. 쿠키 인증 전환 후 실측 필요성이 생기면 후속 |
| `auth.redoceanmap.com` 콜백 방식 | B.0 결정 — 프록시 경로 콜백으로 대체 |
| cloudflared 원격 관리형(대시보드) 마이그레이션 | 로컬 config 관리 유지(비가역 전환 거부, 2026-07-22) |
| www 컨테이너화 | 이번 범위 아님. 호스트 프로세스 전제(A.2 host.docker.internal) |
| 모바일 앱용 토큰 응답 병행 | 클라이언트가 웹뿐. 필요 시 후속 |

## 3. 마이그레이션 주의

- **콘솔 콜백 선등록(§6-1)이 배포보다 먼저다.** 새 콜백 URL을 등록하기 전에 패턴 A를 배포하면 소셜 로그인이 전면 중단된다. 구 URL(`/oauth/*`)은 전환 검증 후 제거.
- 기존 localStorage 토큰 사용자는 전환 시점에 로그아웃 상태가 된다 — 재로그인 1회(사용자 소수, 허용된 비용). 프론트에서 잔존 localStorage 키 정리 코드를 첫 로드에 한 번 실행.
- Part A와 Part B는 독립 — A 먼저(작고 롤백 쉬움), 검증 후 B.

## 4. 수동 작업 (사용자 — 완료 보고서에 그대로 출력)

1. **콘솔 콜백 등록 (B 배포 전):** 네이버·카카오·구글 각각에 추가 —
   `https://redoceanmap.com/api/backend/auth/social/{provider}/callback`, `http://localhost:3000/api/backend/auth/social/{provider}/callback`. 전환 검증 후 기존 `/oauth/{provider}` 3종 제거.
2. **Cloudflare 리다이렉트 룰:** `www.redoceanmap.com/*` → `https://redoceanmap.com/$1` (301) — 쿠키 apex 통일.
3. **env:** `.env.auth`에 `AUTH_PUBLIC_BASE_URL=https://redoceanmap.com` 추가(맥 개발 env는 `http://localhost:3000`). 프론트 배포 env에서 `NEXT_PUBLIC_GOOGLE/KAKAO/NAVER_CLIENT_ID` 제거.
4. **Part A 검증 동행:** 맥에서 `nc -vz <백엔드PC IP> 5432` 실패 확인(포트 잠금 증빙).

## 5. 완료 기준 (Acceptance Criteria)

- [ ] 대시보드 커넥터가 컨테이너 cloudflared 1개, 전 호스트네임 외부 응답 정상, 호스트 cloudflared 서비스 제거됨.
- [ ] compose에 `0.0.0.0` 바인딩 0건, LAN 타 기기에서 5432/6379/8000/9000 접속 불가, 맥 SSH 포워딩·외부 서비스는 정상.
- [ ] 소셜 로그인 3사 전부: start → 프로바이더 → callback → httpOnly 쿠키 → 원래 페이지 복귀 동작.
- [ ] 일반 로그인·리프레시·로그아웃 쿠키 기반 동작, 응답 본문에 토큰 0건.
- [ ] `grep -rn "localStorage" www/lib www/app` 에서 토큰 관련 0건, `tokenStorage.ts` 부재.
- [ ] 신규 쿠키/state 테스트 포함 `pytest` 전체 통과, `lint-imports` 통과.
- [ ] 브라우저 devtools에서 access_token이 JS로 읽히지 않음(`document.cookie`에 미노출) 확인.

## 6. 진행 방식

1. 작업 전 읽기: cloudflared config(실물), `docker-compose.yaml`, `social_router.py`, `social_interactor.py`, `core/security.py`, `www/lib/socialAuth.ts`·`authApi.ts`·`tokenStorage.ts`, `www/next.config.ts` — 현재 상태 요약 보고 후 시작.
2. 커밋 단위(각 커밋에서 전체 동작 유지):
   - ① A.2+A.3 — cloudflared 컨테이너 병행 기동·전환
   - ② A.4 — 포트 잠금
   - ③ B.1+B.2+B.3+B.5(백엔드) — start/callback·쿠키 발급·검증부 (이 시점까지 프론트는 구 흐름으로 동작해야 하므로, 기존 POST 코드 교환 엔드포인트는 ④ 완료까지 유지)
   - ④ B.4 — 프론트 전환 + 구 엔드포인트·콜백 페이지 제거
3. ③→④ 사이에 §4-1 콘솔 등록이 완료되어야 한다 — ④ 시작 전 사용자에게 확인을 요청한다.
