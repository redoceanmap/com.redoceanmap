# CLAUDE.md — auth 앱

백엔드 → [[minseok/_docs/CLAUDE|minseok CLAUDE]]

JWT 기반 인증 스포크. 회원 가입·로그인·토큰 발급을 담당한다.

---

## 역할

- 사용자 계정(`users` 테이블) 영속·조회.
- 비밀번호 해시 검증 + JWT 액세스 토큰 발급(`JWT_SECRET` 환경변수).
- 다른 스포크가 인증이 필요하면 **허브를 경유**한다 — auth를 직접 import하지 않는다(스포크 독립).
- **등급(RBAC 확장, alembic `c3d4e5f6a7b8`)**: `role_tabs`(역할별 노출 탭) 소유. 가입(일반·소셜
  즉시가입·동의 완료) 시 기본 등급 `basic` 자동 부여(`GradeRepository.grant_basic`, 멱등·basic
  부재 시 no-op). 공개 `GET /auth/tabs` — 토큰 유효 시 보유 역할 탭 합집합, 없음/무효 시 basic
  구성 반환. 등급 CRUD는 허브 `GradePolicyPort`를 `GradePolicyGateway`로 구현(어드민 소비).

## 헥사고날 레이어

```
apps/auth/
├── domain/entities/          # User 엔티티 (프레임워크 무의존)
├── app/
│   ├── ports/input/          # AuthUseCase (ABC)
│   ├── ports/output/         # UserRepository (ABC)
│   └── use_cases/            # AuthInteractor
├── adapter/
│   ├── inbound/api/v1/       # auth_router (/auth/*)
│   └── outbound/
│       ├── orm/user_orm.py   # users 테이블 (SQLAlchemy 2.0)
│       └── pg/               # UserPgRepository
└── dependencies/             # DI 프로바이더 (2-function 패턴)
```

**의존 방향:** `adapter → app → domain`. 상세 컨벤션 → [[minseok/_docs/CLAUDE|minseok CLAUDE]].
