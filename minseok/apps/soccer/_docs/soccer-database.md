# Alembic으로 축구 DB 스키마 구축 (pgvector / Ubuntu 26)

> **하네스 원칙(Harness Principle)에 따른 에이전트 작업 지시서**
> - 컨텍스트는 한 번에 필요한 만큼만, 명세는 모호함 없이.
> - 한 번에 한 단계씩 → 각 단계마다 **결정적(deterministic) 검증**으로 되먹임.
> - 검증 실패 시 다음 단계로 진행 금지. 롤백 경로를 항상 확보.
> - 에이전트가 추측하지 않도록 "하지 말 것"을 명시.

---

## 1. Role

너는 PostgreSQL + Alembic 마이그레이션 전문가다. 아래 명세만을 근거로 스키마 마이그레이션을 작성하고, 각 단계를 직접 실행·검증한 뒤 결과를 보고한다. 명세에 없는 사항은 **임의로 추가하지 말고 질문**한다.

## 2. Environment (사실, 추측 금지)

| 항목 | 값 |
|---|---|
| OS | Ubuntu 26 |
| DB | PostgreSQL + `pgvector` 확장 설치됨 |
| 마이그레이션 도구 | Alembic |
| 접속 정보 | 환경변수 `DATABASE_URL` (예: `postgresql+psycopg://user:pw@localhost:5432/soccer`) |
| 대상 스키마 | `public` |

- 접속 정보는 **하드코딩 금지**. `alembic.ini`의 `sqlalchemy.url`은 비워 두고 `env.py`에서 `os.environ["DATABASE_URL"]`로 주입한다.
- `psycopg`(v3) 드라이버 기준. 미설치 시 `pip install alembic "psycopg[binary]" sqlalchemy pgvector` 로 설치한다.

## 3. Target Schema (ERD 명세 — 이대로만 생성)

컬럼 순서·타입·길이를 **그대로** 지킨다. 오탈자처럼 보이는 이름(`statdium_name`)도 ERD 원문 그대로 유지한다.

### 3.1 `stadium`
| 컬럼 | 타입 | 제약 |
|---|---|---|
| `stadium_id` | VARCHAR(10) | **PK** |
| `statdium_name` | VARCHAR(40) | NOT NULL |
| `hometeam_id` | VARCHAR(10) | |
| `seat_count` | INTEGER | |
| `address` | VARCHAR(60) | |
| `ddd` | VARCHAR(10) | |
| `tel` | VARCHAR(10) | |

### 3.2 `team`
| 컬럼 | 타입 | 제약 |
|---|---|---|
| `team_id` | VARCHAR(10) | **PK** |
| `region_name` | VARCHAR(10) | NOT NULL |
| `team_name` | VARCHAR(40) | |
| `e_team_name` | VARCHAR(50) | |
| `orig_yyyy` | VARCHAR(10) | |
| `zip_code1` | VARCHAR(10) | |
| `zip_code2` | VARCHAR(10) | |
| `address` | VARCHAR(80) | |
| `ddd` | VARCHAR(10) | |
| `tel` | VARCHAR(10) | |
| `fax` | VARCHAR(10) | |
| `homepage` | VARCHAR(50) | |
| `owner` | VARCHAR(10) | |
| `stadium_id` | VARCHAR(10) | **FK → stadium.stadium_id** (non-identifying, NULL 허용) |

### 3.3 `player`
| 컬럼 | 타입 | 제약 |
|---|---|---|
| `player_id` | VARCHAR(10) | **PK** |
| `player_name` | VARCHAR(20) | NOT NULL |
| `e_player_name` | VARCHAR(40) | |
| `nickname` | VARCHAR(30) | |
| `join_yyyy` | VARCHAR(10) | |
| `position` | VARCHAR(10) | |
| `back_no` | INTEGER | |
| `nation` | VARCHAR(20) | |
| `birth_date` | DATE | |
| `solar` | VARCHAR(10) | |
| `height` | INTEGER | |
| `weight` | INTEGER | |
| `team_id` | VARCHAR(10) | **FK → team.team_id** (non-identifying, NULL 허용) |

### 3.4 `schedule`
| 컬럼 | 타입 | 제약 |
|---|---|---|
| `sche_date` | VARCHAR(10) | **PK (복합키 1)** |
| `stadium_id` | VARCHAR(10) | **PK (복합키 2) + FK → stadium.stadium_id** (identifying) |
| `gubun` | VARCHAR(10) | |
| `hometeam_id` | VARCHAR(10) | |
| `awayteam_id` | VARCHAR(10) | |
| `home_score` | INTEGER | |
| `away_score` | INTEGER | |

### 3.5 관계 요약
```
stadium (1) ──< schedule   : schedule.stadium_id → stadium.stadium_id  (PK 구성, identifying)
stadium (1) ──< team       : team.stadium_id     → stadium.stadium_id  (non-identifying)
team    (1) ──< player     : player.team_id      → team.team_id        (non-identifying)
```
- FK는 모두 `ON DELETE RESTRICT ON UPDATE CASCADE`.
- FK 컬럼(`team.stadium_id`, `player.team_id`, `schedule.stadium_id`)에는 인덱스를 생성한다.
- 생성 순서: `stadium` → `team` → `player` → `schedule`. `downgrade()`는 역순.

## 4. Task (순서대로, 한 단계씩)

1. **초기화 점검** — `alembic` 디렉터리가 없으면 `alembic init migrations`. 이미 있으면 재초기화하지 말고 기존 구성을 읽는다.
2. **env.py 구성** — `DATABASE_URL` 주입, `target_metadata` 연결, `compare_type=True`.
3. **Revision 1: `enable_pgvector`** — `CREATE EXTENSION IF NOT EXISTS vector;` / downgrade는 `DROP EXTENSION IF EXISTS vector;`
   - ERD에는 벡터 컬럼이 없다. **임베딩 컬럼을 임의로 추가하지 말 것.** 확장 활성화만 한다.
4. **Revision 2: `create_soccer_schema`** — 3장의 4개 테이블·PK·FK·인덱스를 `op.create_table` / `op.create_index`로 작성. `down_revision`을 Revision 1에 연결.
5. **적용** — `alembic upgrade head` 실행.
6. **검증** — 아래 5장의 명령을 모두 실행하고 출력을 그대로 보고한다.
7. **롤백 리허설** — `alembic downgrade base` → `alembic upgrade head` 를 1회 왕복 실행해 두 방향 모두 오류 없이 동작함을 증명한다.

## 5. Verification (통과해야 완료)

```bash
alembic current          # head 리비전이 표시될 것
alembic history --verbose
psql "$DATABASE_URL" -c "\dt"
psql "$DATABASE_URL" -c "\d stadium"
psql "$DATABASE_URL" -c "\d team"
psql "$DATABASE_URL" -c "\d player"
psql "$DATABASE_URL" -c "\d schedule"
psql "$DATABASE_URL" -c "SELECT extname FROM pg_extension WHERE extname='vector';"
psql "$DATABASE_URL" -c "
SELECT conrelid::regclass AS tbl, conname, pg_get_constraintdef(oid)
FROM pg_constraint WHERE contype IN ('p','f')
  AND conrelid::regclass::text IN ('stadium','team','player','schedule')
ORDER BY 1;"
```

**Definition of Done**
- [ ] 4개 테이블이 명세와 컬럼명·타입·길이가 100% 일치
- [ ] `schedule` PK가 `(sche_date, stadium_id)` 복합키
- [ ] FK 3개가 정확한 대상 테이블을 가리킴
- [ ] `vector` 확장이 활성 상태
- [ ] `downgrade base` → `upgrade head` 왕복 성공
- [ ] 위 검증 명령 출력 전문을 보고에 포함

## 6. Guardrails (하지 말 것)

- ERD에 없는 테이블·컬럼·시퀀스·트리거·기본값을 **추가하지 말 것** (`created_at` 같은 것 포함).
- 컬럼명 오탈자(`statdium_name`)를 임의로 "수정"하지 말 것.
- `DROP DATABASE`, `TRUNCATE`, 기존 데이터를 파괴하는 명령 금지.
- `alembic revision --autogenerate`에만 의존하지 말 것 — 생성된 파일을 반드시 열어 명세와 대조 후 수정.
- 마이그레이션 파일을 한 번에 여러 개 만들지 말고, 4→5→6 단계를 통과한 뒤 다음으로 넘어갈 것.
- 검증 실패 시 임의 우회 금지. 실패 로그를 그대로 보고하고 원인을 먼저 설명할 것.

## 7. Report Format (작업 종료 시)

```
1) 생성/수정한 파일 목록
2) 각 마이그레이션의 revision id와 down_revision 체인
3) 5장 검증 명령의 실제 출력
4) Definition of Done 체크 결과
5) 남은 이슈 / 확인이 필요한 질문
```