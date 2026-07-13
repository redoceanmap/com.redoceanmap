# PROMPT — market 3NF 스키마 Alembic 초기 마이그레이션 (Docker 실행)

> Claude Code 하네스 프롬프트. 한 번 쓰고 버리는 대화가 아니라 **버전 관리되는 스펙**이다.
> 실행 결과가 기대와 다르면 프롬프트를 고치고 다시 돌린다 (대화로 땜빵하지 않는다).

---

## 0. 하네스 규약 (Harness Contract)

| 항목 | 값 |
|------|-----|
| 목표 | `MARKET_ERD.md`의 3NF 스키마(차원 5 + 팩트 8 + 벤치마크 1)를 **Docker 컨테이너 안의 pgvector Postgres**에 Alembic 마이그레이션으로 생성 |
| 진실의 원천(SoT) | ① `adapter/outbound/orm/` (SQLAlchemy 2.0 `Mapped`) ② `_docs/MARKET_ERD.md` — **충돌 시 ORM 코드가 우선**, 불일치는 보고만 하고 임의 수정 금지 |
| 산출물 | ① `docker-compose.yml` (또는 기존 파일에 `db` 서비스 추가) ② `.env.example` ③ `alembic/versions/*_init_market_3nf.py` ④ (필요 시) `alembic.ini` / `env.py` 패치 |
| 검증 루프 | 컨테이너 기동 → `upgrade head` → 컨테이너 내부 psql로 스키마 실측 → `downgrade base` → 재 `upgrade head` 무오류 통과 |
| 종료 조건 | 아래 §7 Definition of Done 전 항목 ✅ |
| 금지 | 호스트에 Postgres 직접 설치(`apt install postgresql`), 스키마 추측/창작, ORM 모델 임의 수정, `--autogenerate` 결과 무검증 커밋, 프로덕션 DB 접속 |

---

## 1. 환경 (Environment)

- 호스트 OS: **Ubuntu 26.x**
- **DB는 호스트에 설치하지 않는다. 반드시 Docker 컨테이너 안에서만 구동한다.**
- 이미지: `pgvector/pgvector:pg17` (pgvector 확장이 내장된 공식 Postgres 이미지)
- Python: SQLAlchemy **2.0** (`Mapped[...]` / `mapped_column`), Alembic, psycopg(v3) 또는 psycopg2 — **호스트(또는 앱 컨테이너)에서 실행**, DB 컨테이너에는 파이썬을 넣지 않는다.
- 프로젝트 구조: 헥사고날 — ORM은 `adapter/outbound/orm/`, 적재 스크립트는 `scripts/ingest_seoul_3nf.py`, 컬럼 매핑은 `adapter/outbound/csv/column_maps.py`.

### pgvector에 대한 주의
현재 ERD에는 **벡터 컬럼이 존재하지 않는다.** pgvector는 "pgvector 확장을 갖춘 Postgres 이미지"라는 의미로만 취급한다.
- 마이그레이션 첫 단계에서 `CREATE EXTENSION IF NOT EXISTS vector;` 만 실행한다.
- **임의로 `embedding VECTOR(n)` 컬럼이나 HNSW/IVFFlat 인덱스를 추가하지 말 것.** 필요하면 별도 후속 마이그레이션으로 제안만 한다.

---

## 2. Docker 준비 (DB는 컨테이너 안에서)

### 2.1 사전 확인
```bash
docker --version && docker compose version   # 없으면 설치 안내만 하고 중단
docker ps                                    # 5432 포트 충돌 여부 확인
ss -ltnp | grep 5432 || true                 # 호스트에 이미 떠 있는 Postgres 있으면 포트 변경 제안
```
> 호스트 5432가 이미 사용 중이면 **호스트에 깔린 Postgres를 죽이지 말고**, compose의 호스트 포트를 `5433`으로 바꾸고 `DATABASE_URL`도 맞춰 수정한다.

### 2.2 `docker-compose.yml` (없으면 생성, 있으면 `db` 서비스만 추가)

```yaml
services:
  db:
    image: pgvector/pgvector:pg17
    container_name: market-pgvector
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-market}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?set in .env}
      POSTGRES_DB: ${POSTGRES_DB:-market}
      TZ: Asia/Seoul
    ports:
      - "${DB_PORT:-5432}:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-market} -d ${POSTGRES_DB:-market}"]
      interval: 5s
      timeout: 3s
      retries: 10

volumes:
  pgdata:
```

요구사항:
- 비밀번호는 **`.env`에서만** 주입. compose/코드에 하드코딩 금지. `.env`는 `.gitignore`에, `.env.example`만 커밋.
- 데이터는 **named volume `pgdata`** 에 영속. bind mount로 호스트 경로를 쓰지 않는다(우분투 권한 이슈 회피).
- `CREATE EXTENSION`은 **Alembic 마이그레이션이 담당**한다. `docker-entrypoint-initdb.d/*.sql`로 스키마를 만들지 말 것 — 스키마의 단일 출처는 Alembic이다.

### 2.3 `.env.example`
```dotenv
POSTGRES_USER=market
POSTGRES_PASSWORD=change-me
POSTGRES_DB=market
DB_PORT=5432
# 호스트에서 alembic 실행 시
DATABASE_URL=postgresql+psycopg://market:change-me@localhost:5432/market
```

### 2.4 기동 & 준비 대기
```bash
docker compose up -d db
docker compose ps                                   # healthy 될 때까지 대기
until docker compose exec -T db pg_isready -U "${POSTGRES_USER:-market}"; do sleep 1; done
docker compose exec -T db psql -U market -d market -c "SELECT version();"
```

---

## 3. 사전 조사 (Read before you write)

아래를 **먼저 읽고**, 발견한 사실을 짧게 요약한 뒤에 코드를 쓴다.

1. `adapter/outbound/orm/` 전체 — Base 위치, `MarketStatMixin`, 각 모델의 테이블명/컬럼명/타입/nullable/UniqueConstraint/Index.
2. 기존 `docker-compose.yml` / `Dockerfile` 유무 — 있으면 **덮어쓰지 말고 `db` 서비스만 병합**.
3. `alembic/` 존재 여부 — 없으면 `alembic init`. 있으면 `env.py`가 `Base.metadata`를 물고 있는지 확인.
4. `_docs/MARKET_ERD.md` — 관계와 제약명 확인용.
5. 기존 `alembic/versions/` 이력 — 초기 리비전이 이미 있으면 **덮어쓰지 말고 보고**.

---

## 4. 작업 (Task)

### 4.1 Alembic 배선
- `alembic/env.py`: `target_metadata = Base.metadata` (ORM Base import).
- `sqlalchemy.url`은 `alembic.ini` 하드코딩 대신 `env.py`에서 `os.environ["DATABASE_URL"]`로 주입.
- `context.configure(..., compare_type=True, compare_server_default=True)`.

### 4.2 초기 리비전 생성
```bash
alembic revision --autogenerate -m "init market 3nf"
```
autogenerate 결과를 **그대로 믿지 말고** §5 체크리스트로 손보정한다.

### 4.3 마이그레이션 본문 요구사항

**실행 순서 (upgrade)**
1. `op.execute("CREATE EXTENSION IF NOT EXISTS vector")`
2. 차원: `region` → `trade_area_division` → `service_category` → `change_indicator` → `trade_area`
3. 팩트 8: `estimated_sales`, `store`, `floating_population`, `resident_population`, `working_population`, `consumption`, `apartment`, `commercial_change`
4. `commercial_change_benchmark`

`downgrade`는 정확한 **역순**. extension은 drop하지 않는다.

**테이블별 필수 사항**

| 테이블 | 반드시 지킬 것 |
|--------|----------------|
| `region` | PK `code` varchar(20). **자기참조 FK** `parent_code → region.code` — `sa.ForeignKeyConstraint(..., use_alter=True)` 또는 테이블 생성 후 `op.create_foreign_key`로 분리. `level`(0 시도/1 자치구/2 행정동), x/y_coord·area_size는 nullable. |
| `trade_area` | PK `code` **int** (상권_코드, 자연키). `division_code` FK(NOT NULL), `region_code` FK → region.code (nullable). `lat`/`lng`는 파이썬 property이므로 **컬럼으로 만들지 말 것**. |
| 팩트 8 공통 | `id` int PK(자동증가) + `year_quarter` int + `trdar_code` int FK → `trade_area.code`. `year_quarter`, `trdar_code`, 팩트별 FK에 **index**. |
| 유니크 제약 | 제약명 **정확히 일치**: `uq_estimated_sales`, `uq_store`, `uq_floating_population`, `uq_resident_population`, `uq_working_population`, `uq_consumption`, `uq_apartment`, `uq_commercial_change`, `uq_commercial_change_benchmark`. 조합은 매출/점포만 (year_quarter, trdar_code, service_code), 나머지 (year_quarter, trdar_code), 벤치마크 (year_quarter, region_code). |
| `estimated_sales` | 금액 `BigInteger`, 건수 `Integer`. 월간/주중·주말/요일7/시간대6/성별2/연령대6 각각 amount·count 쌍. 분해 컬럼은 **넓게 유지**(행 분리 금지). |
| `consumption` | 전 측정 컬럼 nullable, 소득·지출 float. |
| `apartment` | 면적별 5 · 가격별 7 세대수 nullable, `avg_price`는 **BigInteger**. |
| `commercial_change` | `change_indicator` varchar FK → `change_indicator.code`. |
| `commercial_change_benchmark` | 상권 팩트가 아님 — `trdar_code` 없음. `region_code` FK(시도 레벨). |

**타입 매핑**: `int` → `sa.Integer`, `bigint` → `sa.BigInteger`, `float` → `sa.Float`(금액성이면 `sa.Numeric` 제안만 하고 ORM을 따른다), `varchar(n)` → `sa.String(n)`.

---

## 5. 자가 점검 체크리스트 (autogenerate 이후 반드시 수행)

- [ ] DB가 **컨테이너 안에서만** 돌고 있는가 (`docker compose ps`로 확인, 호스트 설치 흔적 없음)
- [ ] `region.parent_code` 자기참조 FK가 순환 없이 생성/삭제되는가 (`use_alter`)
- [ ] `trade_area.code`가 int PK이고, 8개 팩트의 `trdar_code`가 전부 이를 참조하는가
- [ ] 제약명이 ERD 명칭과 문자 단위로 일치하는가 (Alembic 자동명명에 맡기지 않았는가)
- [ ] `lat`/`lng` 등 ORM property가 컬럼으로 새어 들어가지 않았는가
- [ ] nullable 여부가 ORM과 1:1로 일치하는가 (consumption·apartment의 ✓ 컬럼)
- [ ] `downgrade`가 FK 의존 역순인가
- [ ] 마이그레이션에 서울 하드코딩(`'11'`, '서울' 등 데이터 값)이 없는가 — **DDL만, 데이터 시드 금지**
- [ ] 비밀번호가 compose/코드/마이그레이션 어디에도 평문으로 남지 않았는가

---

## 6. 검증 (Verification Loop)

```bash
# 0) 컨테이너 기동 및 헬스체크
docker compose up -d db
until docker compose exec -T db pg_isready -U market; do sleep 1; done

# 1) 상향 (호스트에서 실행, DATABASE_URL은 localhost:5432)
alembic upgrade head

# 2) 컨테이너 내부에서 스키마 실측
docker compose exec -T db psql -U market -d market -c "\dt"          # 14개 테이블 + alembic_version
docker compose exec -T db psql -U market -d market -c "\d+ trade_area"
docker compose exec -T db psql -U market -d market -c "\d+ estimated_sales"
docker compose exec -T db psql -U market -d market -c \
  "SELECT conname FROM pg_constraint WHERE conname LIKE 'uq_%' ORDER BY 1;"   # 9개
docker compose exec -T db psql -U market -d market -c \
  "SELECT extname FROM pg_extension;"                                          # vector 포함
docker compose exec -T db psql -U market -d market -c \
  "SELECT count(*) FROM information_schema.columns WHERE table_name='estimated_sales';"

# 3) drift 0 확인 — 생성된 마이그레이션이 비어 있어야 정상 (확인 후 삭제)
alembic revision --autogenerate -m "drift check"

# 4) 왕복
alembic downgrade base && alembic upgrade head

# 5) 영속성 — 컨테이너 재기동해도 스키마 유지
docker compose restart db && sleep 5
docker compose exec -T db psql -U market -d market -c "\dt"

# 6) 클린룸 재현 — 볼륨까지 날리고 처음부터 성공해야 한다
docker compose down -v && docker compose up -d db
until docker compose exec -T db pg_isready -U market; do sleep 1; done
alembic upgrade head
```

실패하면 **compose/마이그레이션 파일을 고쳐 0~6을 반복**한다. 컨테이너에 들어가 수동 SQL로 DB를 손보고 넘어가지 않는다.

---

## 7. Definition of Done

1. `docker compose up -d db` 만으로 pgvector Postgres가 healthy 상태로 뜬다. **호스트에는 Postgres를 설치하지 않았다.**
2. `alembic upgrade head`가 빈 DB에서 무오류 통과.
3. 테이블 14개 = 차원 5 + 팩트 8 + 벤치마크 1, 전부 생성됨.
4. `alembic revision --autogenerate` 재실행 시 **diff 없음**(빈 마이그레이션).
5. `downgrade base` → `upgrade head` 왕복 성공.
6. 유니크 제약 9개 이름이 ERD와 일치.
7. `docker compose down -v` 후 재기동 → `upgrade head` **클린룸 재현 성공**.
8. `vector` extension 설치 확인. **벡터 컬럼은 추가되지 않음.**
9. 변경 파일 목록 + ERD ↔ ORM 불일치 발견 사항을 **마지막에 요약 보고**.

---

## 8. Out of Scope (하지 말 것)

- 호스트에 Postgres/pgvector 직접 설치 (`apt install postgresql*`, 소스 빌드).
- `docker-entrypoint-initdb.d`에 스키마 SQL 넣기 (스키마 출처는 Alembic 단일화).
- CSV 적재 (`scripts/ingest_seoul_3nf.py` 실행) — 별도 태스크.
- ORM 모델 리팩터링, 컬럼 추가/삭제.
- 임베딩/벡터 인덱스(HNSW·IVFFlat) 설계.
- 프로덕션 DB 접속 및 마이그레이션 적용.