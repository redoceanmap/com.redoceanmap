# CLAUDE.md — mail 앱

백엔드 → [[minseok/_docs/CLAUDE|minseok CLAUDE]]

수신 메일 저장·조회 스포크 (ragwatson sherlock_homes의 inbound mail 이식).
Gmail → (Pub/Sub 또는 폴링) → n8n → 허브 `/automation/mail` → 이 앱이 영속화한다.
n8n·Gmail의 존재는 모른다 — 허브 `MailStoragePort`의 구현만 제공한다.

---

## 역할

- `InboundMailInteractor`(대장): **임베딩 생성 → 저장**(message_id 중복 무시)·최신순 조회·의미 검색.
- **pgvector 임베딩**: 수신 시 제목+본문을 bge-m3(1024차원)로 임베딩해 `embedding` 컬럼에
  저장(오케스트레이터 `embed()`로 수렴). 임베딩 실패 시 NULL로 저장 — 수신이 우선.
  `GET /mail/search?q=` 가 질의를 임베딩해 코사인 유사도 순으로 반환.
- **수신 경로**: n8n → 허브 `POST /automation/mail` → `MailStoragePort` → `MailStorageGateway`
  → **왓처 관문**(`screen_and_receive`: 유해 메일 차단·기록, 정상만 통과) → `inbound_mails` 테이블.
- **조회**: `GET /mail/list` (액터: 사용자/프론트 — 이 앱 소유 라우터).
- **유해 스크리닝(v1)**: `POST /watcher/screen` — KcELECTRA-base + Unsmile 파인튜닝
  (`scripts/train_moderation_v1.py` → `models/moderation/kcelectra-unsmile-v1`, gitignore).
  ModerationPort(점수) → domain `moderation_policy.judge`(정책: 유해 9카테고리·임계값 0.5).
  검증 macro-F1 0.707. 모델 교체는 어댑터만(Kanana Safeguard 등으로 확장 예정).
- **문서**: 수신 파이프라인 구축·운영 → [[minseok/apps/mail/_docs/gmail-n8n-runbook|gmail-n8n-runbook]]
  (적용 현황 표 포함) · 분류/격상 설계안 → [[minseok/apps/mail/_docs/watcher_router|watcher_router]]
  · 에이전트 DTO 배역 설계안 → [[minseok/apps/mail/_docs/mail-agent-casting|mail-agent-casting]].

## 레이어

```
apps/mail/
├── domain/entities/inbound_mail.py            # InboundMail (frozen, message_id 유니크)
├── app/
│   ├── ports/input/inbound_mail_use_case.py
│   ├── ports/output/{inbound_mail_repository,embedding_port}.py
│   └── use_cases/inbound_mail_interactor.py   # 대장
├── adapter/
│   ├── inbound/api/v1/mail_router.py          # GET /mail/list · /mail/search(의미 검색)
│   └── outbound/
│       ├── orm/inbound_mail_orm.py            # inbound_mails (embedding vector(1024))
│       ├── ai/ollama_embedding_adapter.py      # EmbeddingPort 구현 (bge-m3)
│       ├── pg/inbound_mail_pg_repository.py
│       └── gateways/mail_storage_gateway.py   # 허브 MailStoragePort 구현
├── dependencies/mail_provider.py
└── tests/
```

**의존 방향:** `adapter → app → domain`. 컨벤션 → [[minseok/_docs/CLAUDE|minseok CLAUDE]].
