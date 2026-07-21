# CLAUDE.md — admin 앱

백엔드 → [[minseok/_docs/CLAUDE|minseok CLAUDE]]

운영 콘솔(어드민) 스포크. 회원·상권·추천·데이터셋 현황을 열람하고 역할(RBAC)을 부여/회수한다.
**자체 ORM/DB가 없다** — 모든 데이터는 허브 포트 3개를 경유해 소유 스포크(auth·market·recommendation)에서 온다.

---

## 역할

- `/admin/*` 엔드포인트 표면 소유. 인증(JWT)은 main.py 공통, 권한은 엔드포인트 단
  `require_permission("<code>")`(core/security — 매 요청 DB 조회라 역할 회수 즉시 반영).
- 프론트 `/admin` 가드 판정: `GET /admin/me` — 호출자의 permission 코드 목록(빈 배열 = 비관리자).
- 권한 코드 6종: `dashboard:read` · `areas:read` · `members:read` · `members:write` ·
  `recommendations:read` · `datasources:read`. RBAC 테이블(roles 등 4종)은 **auth 소유**,
  시드는 alembic `f0a1b2c3d4e5`, 최초 부여는 `scripts/grant_admin.py <email>`.

## 슬라이스 (1:1 컨벤션)

| 슬라이스 | 엔드포인트 | 소비 허브 포트 |
|---|---|---|
| steward (페르소나) | GET /admin/myself · GET /admin/me | MemberDirectoryPort |
| dashboard | GET /admin/dashboard | MemberDirectory + RecommendationDirectory + CommercialData |
| member | GET /admin/members · GET /admin/members/roles · POST /admin/members/{id}/roles · DELETE /admin/members/{id}/roles/{code} | MemberDirectoryPort |
| area | GET /admin/areas | CommercialDataPort (get_area_overview) |
| recommendation_log | GET /admin/recommendations | RecommendationDirectoryPort |
| data_source | GET /admin/data-sources | CommercialData (get_dataset_stats) + RecommendationDirectory |

인터랙터는 허브 포트를 생성자 주입받고, 프로바이더는 허브 스텁 프로바이더를 `Depends`로 받는다
(합성 루트 main.py의 `dependency_overrides`가 스포크 게이트웨이로 치환 — 계약 상세는 hub CLAUDE).

## 레이어

```
apps/admin/
├── app/
│   ├── dtos/{steward,dashboard,member,area,recommendation_log,data_source}_dto.py
│   ├── ports/input/{...}_use_case.py            # 슬라이스별 UseCase ABC
│   ├── ports/output/steward_record_port.py      # steward 활동 기록(유일한 자체 아웃바운드 포트)
│   └── use_cases/{...}_interactor.py
├── adapter/
│   ├── inbound/api/{schemas,v1}/{...}_{schema,router}.py
│   └── outbound/log_steward_record_adapter.py   # 임시 로그 구현
├── dependencies/{...}_provider.py
└── tests/app/use_cases/test_{...}_interactor.py # 스텁 허브 포트로 검증
```

**의존 방향:** `adapter → app → domain`. 컨벤션 → [[minseok/_docs/CLAUDE|minseok CLAUDE]].
