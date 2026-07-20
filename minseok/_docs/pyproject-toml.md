# Harness: `exaone-a2a-portfolio` 프로젝트 스캐폴딩

> 이 문서는 Claude Code에 그대로 전달하는 작업 지시서(harness)입니다.
> 목표는 아래 아키텍처에 맞는 **`pyproject.toml` 생성 + 최소 디렉터리 스캐폴딩**입니다.
> 애매하면 추측하지 말고, 이 문서의 "제약(Constraints)"을 우선하세요.
>
> **주의:** `exaone-a2a-portfolio`는 `com.redoceanmap` 모노레포와 **별개의 독립 저장소**다.
> minseok의 스타 토폴로지·헥사고날·importlinter 규칙은 이 프로젝트에 적용되지 않는다.
> (단, Ollama 데몬은 redoceanmap 백엔드와 **공유**한다 — 0장 참고.)

---

## 0. 프로젝트 상태 점검 결과 (2026-07-20, 백엔드 PC에서 실측)

| 항목 | 문서 전제 | 실측 | 판정 |
|---|---|---|---|
| GPU | RTX 3050 8GB | NVIDIA GeForce RTX 3050, 8192 MiB (WSL2) | ✅ 일치 |
| 추론 모델 | EXAONE 3.5 7.8B Q4_K_M ≈4.77GB | `exaone3.5:7.8b` 4.8GB — **이미 Ollama에 설치됨** | ✅ 일치 |
| OS | 온프레미스 Ubuntu | **Ubuntu on WSL2** (Windows 호스트) | ⚠️ 보정 — NAT 이중화, 아래 참고 |
| 시스템 RAM | "16GB 타이트, 32GB 편함" | **WSL2 할당 총 7GB, 가용 ~5GB** | ❌ 보정 필수 — 아래 자원 주의 참고 |
| VRAM 상주 | EXAONE 단독 ≈4.77GB | EXAONE 4.8GB + `bge-m3` 1.2GB (기존 크론용) = **≈6GB/8GB** | ⚠️ 여유 ~2GB, 참고만 |
| uv | 전제 | uv 0.11.28 설치됨 | ✅ |
| Python | `>=3.12` | 호스트 3.14.4 (uv가 버전 관리) | ✅ 충족 |
| 단일 모델 인스턴스 | 설계 결정 #1 | redoceanmap **단일 모델 정책(2026-07-15)**으로 이미 운영 중 | ✅ 기존 정책과 정합 |

실측이 문서 전제와 다른 지점은 본문(1장 자원 주의)에 보정해 두었다.

---

## 1. 프로젝트 목표

개인 포트폴리오용 멀티에이전트 시스템. 비즈니스가 아니라 **A2A · MCP · 그래프DB 3계층을 직접 구현해 보이는 것**이 목적.

- **온프레미스(Ubuntu on WSL2 + RTX 3050 8GB)**: EXAONE 3.5 7.8B(`exaone3.5:7.8b`)로 실제 GPU 추론. 논리적 에이전트 2개. **유일한 백엔드/추론 머신.**
- **AWS**: 오케스트레이션/라우팅만. **LLM·GPU 의존성 없음** (비용 최소화).
- **Vercel**: 결과를 표시하는 프런트엔드(Next.js, TypeScript — 이 pyproject 범위 밖).
- **에이전트 간 통신**: A2A (`a2a-sdk`).
- **에이전트 ↔ 도구/데이터**: MCP (`mcp`).
- **메모리/지식 저장소**: Neo4j 그래프DB, MCP 서버로 감싸서 노출.

데이터 흐름:
```
Vercel(UI) → AWS(오케스트레이터, A2A 클라이언트/서버, AI 없음)
           → 큐/터널 → 온프레(EXAONE 에이전트 A·B, A2A 서버)
           → MCP → Neo4j(그래프DB)
           → 결과 push → AWS → Vercel
```

### 머신별 역할 · 설치/실행 위치 (중요)

컴포넌트를 아무 머신에서나 설치·실행하지 말 것. 아래 매핑을 따른다.

| 머신 | 역할 | 설치(extra) | 실행하는 것 |
|---|---|---|---|
| **Ubuntu on WSL2 + RTX 3050 8GB** | 유일한 백엔드/추론 머신 | `.[onprem]` + `.[mcp-neo4j]` (= `.[all]` 가능) + `dev` | Ollama(EXAONE), 에이전트 A·B, MCP-Neo4j 서버, Neo4j DB |
| **AWS** | 오케스트레이션/라우팅. **AI 없음** | `.[aws]` 만 | orchestrator |
| **Vercel** | 프런트엔드(Next.js/TS) | — (pyproject 범위 밖) | UI |
| **맥북(M4 16GB)** | 개발/접속용 터미널. **추론 안 함** | `dev` 그룹만 (원하면 `ruff`/`mypy` 로컬 실행용) | 코드 편집·git·SSH·Claude Code |

- **`uv sync --extra all` 은 반드시 백엔드 PC(WSL2)에서.** 맥북에서 돌릴 필요 없음.
- 맥북↔PC는 같은 LAN → SSH 원격 개발(VS Code Remote-SSH / Cursor) 권장. **Claude Code도 코드가 실제로 도는 백엔드 PC 쪽에서 실행**하는 게 실행/디버깅 루프상 가장 깔끔.
- `ollama` 파이썬 패키지는 얇은 HTTP 클라이언트라 맥에 깔려도 무해(로컬 모델이 없을 뿐). 맥에서 `ruff`/`mypy`는 문제없이 동작.

### 단일 백엔드 PC의 자원 주의 (VRAM보다 시스템 RAM — 실측 반영)

**VRAM (8GB):** EXAONE Q4_K_M 4.8GB에 더해 redoceanmap 크론이 쓰는 `bge-m3`(1.2GB)가 함께 상주한다.
합계 ≈6GB로 여유는 ~2GB — 아직 문제는 아니지만 "EXAONE만 올라간다"는 전제는 이 PC에선 성립하지 않는다.

**시스템 RAM — 진짜 병목 (실측: WSL2 총 7GB, 가용 ~5GB):**
Neo4j(힙+페이지캐시) + 에이전트 2개 프로세스 + MCP 서버 + 기존 redoceanmap 스택(FastAPI·PG 도커·크론)이
전부 이 7GB를 나눠 쓴다. 문서 원안의 "16GB 타이트" 기준으로 보면 현재 할당은 **부족**하다.

- **1순위 조치: Windows `.wslconfig`의 `memory=`를 상향**(호스트 여유에 따라 12~16GB 권장) 후 `wsl --shutdown`으로 재기동.
- Neo4j 힙 상한은 원안(1G)보다 낮게 시작: `NEO4J_server_memory_heap_max__size=512m`,
  페이지캐시 `NEO4J_server_memory_pagecache_size=256m` (배포 문서/compose에 반영). RAM 상향 후 1G로 완화.
- 포트폴리오 데모 중에는 redoceanmap 크론(특히 02:30 라벨링)과 GPU/RAM을 공유한다는 점을 기억할 것 —
  데모 시간대를 크론과 겹치지 않게 잡는다.

---

## 2. 핵심 설계 결정 (그대로 지킬 것)

1. **모델 인스턴스는 1개, 에이전트는 2개.**
   에이전트 A·B는 각자 EXAONE를 VRAM에 따로 올리지 않는다. Ollama(또는 MLX) 서버 **하나**가 모델을 한 번만 로드하고, 에이전트 A·B는 서로 다른 시스템 프롬프트/역할/툴셋으로 같은 모델 엔드포인트에 요청한다. (RTX 3050 8GB / M4 16GB 모두 단일 인스턴스 전제.)
   → 이 결정은 redoceanmap의 **단일 모델 정책(EXAONE 7.8B만, 2026-07-15)**과 동일 노선이며, 이 PC의 Ollama 데몬(systemd, `0.0.0.0` 바인딩)을 **새로 띄우지 말고 그대로 재사용**한다. 새 Ollama 인스턴스·새 모델 태그 추가 금지.

2. **AWS 컴포넌트는 AI 의존성을 절대 포함하지 않는다.**
   `ollama`, `neo4j`, `torch`, 모델 관련 패키지는 `aws` extra에 넣지 말 것. AWS 배포 시 `pip install .[aws]`만으로 가볍게 설치돼야 한다.

3. **의존성은 배포 타깃별 optional-dependencies로 격리한다.**
   base(공통) → `onprem` / `aws` / `mcp-neo4j` extra. dev 도구는 PEP 735 `[dependency-groups]`.

4. **NAT 뒤 온프레는 outbound 연결만.** AWS가 집 네트워크로 직접 인바운드하지 않는다.
   이 PC는 **WSL2라 NAT가 이중**(공유기 NAT + WSL2 NAT)이므로 인바운드 포워딩은 사실상 배제하고,
   터널/큐 폴링(outbound-only)이 선택이 아니라 **필수**다. (코드가 아니라 배포 문서에 남길 것.)

---

## 3. 생성할 디렉터리 구조

```
exaone-a2a-portfolio/
├── pyproject.toml            # ← 이 문서의 4장 내용 그대로
├── README.md                 # 짧은 소개 + 실행법 (직접 작성)
├── .gitignore                # python + node 표준
├── src/
│   └── exaone_a2a/
│       ├── __init__.py
│       ├── config.py         # pydantic-settings 기반 공통 설정
│       ├── onprem/
│       │   ├── __init__.py
│       │   ├── agent_a/
│       │   │   ├── __init__.py
│       │   │   └── __main__.py   # A2A 서버 엔트리 (스텁 OK)
│       │   └── agent_b/
│       │       ├── __init__.py
│       │       └── __main__.py
│       ├── aws/
│       │   ├── __init__.py
│       │   └── orchestrator/
│       │       ├── __init__.py
│       │       └── __main__.py   # A2A 라우팅 + 큐, AI 없음
│       └── mcp_neo4j/
│           ├── __init__.py
│           └── server.py         # Neo4j MCP 서버 (스텁 OK)
└── tests/
    └── test_smoke.py         # import 스모크 테스트
```

각 `__main__.py` / `server.py`는 지금은 **동작하는 최소 스텁**(엔트리포인트 함수 `main()` 정의 + `if __name__ == "__main__"`)이면 충분하다. 실제 에이전트 로직은 다음 단계.

---

## 4. `pyproject.toml` (이 내용으로 생성)

```toml
[project]
name = "exaone-a2a-portfolio"
version = "0.1.0"
description = "Personal portfolio: A2A multi-agent system with on-prem EXAONE 7.8B, AWS orchestration (no AI), and a Neo4j graph DB exposed over MCP."
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }
authors = [{ name = "Minseok Jang" }]
keywords = ["a2a", "mcp", "agents", "exaone", "neo4j", "ollama"]

# 공통(base) 의존성만. 배포 타깃별 무거운 패키지는 아래 optional-dependencies로.
dependencies = [
    "pydantic>=2.9",
    "pydantic-settings>=2.6",
    "httpx>=0.27",
    "structlog>=24.4",
]

[project.optional-dependencies]
# 온프레: 실제 추론 + A2A 서버 + MCP 클라이언트
onprem = [
    "a2a-sdk[http-server]>=1.1.1",
    "ollama>=0.4",
    "mcp>=1.2",
]

# AWS: 오케스트레이션/라우팅만. AI·GPU 의존성 금지.
aws = [
    "a2a-sdk[http-server]>=1.1.1",
    "boto3>=1.35",
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",
]

# Neo4j를 감싸는 MCP 서버
mcp-neo4j = [
    "mcp>=1.2",
    "neo4j>=5.26",
]

# 로컬 개발용 올인원 (온프레 개발 머신 기준)
all = [
    "exaone-a2a-portfolio[onprem,aws,mcp-neo4j]",
]

[project.scripts]
onprem-agent-a  = "exaone_a2a.onprem.agent_a.__main__:main"
onprem-agent-b  = "exaone_a2a.onprem.agent_b.__main__:main"
aws-orchestrator = "exaone_a2a.aws.orchestrator.__main__:main"
mcp-neo4j        = "exaone_a2a.mcp_neo4j.server:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/exaone_a2a"]

# 개발 도구는 배포 extra가 아니라 dependency-group (PEP 735, uv 기본 지원)
[dependency-groups]
dev = [
    "ruff>=0.8",
    "mypy>=1.13",
    "pytest>=8.3",
    "pytest-asyncio>=0.24",
    "anyio>=4.6",
]

[tool.ruff]
line-length = 100
target-version = "py312"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "ASYNC"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.mypy]
python_version = "3.12"
strict = true
files = ["src", "tests"]
```

---

## 5. 실행/검증 명령 (uv 기준)

프로젝트 생성 후 아래가 통과해야 한다. (백엔드 PC에 uv 0.11.28 설치 확인됨.
호스트 Python은 3.14이지만 `requires-python >= 3.12`는 uv가 알아서 충족시킨다.)

```bash
# 온프레 개발 머신: 전체 설치 + dev 그룹
uv sync --extra all

# AWS 배포 시뮬레이션: aws extra만 설치되고 ai 패키지가 없어야 함
uv pip install ".[aws]"
python -c "import a2a, boto3, fastapi"           # OK
python -c "import ollama" && echo "FAIL: aws에 ollama가 들어감" || echo "OK: ai 없음"

# 품질 게이트
uv run ruff check .
uv run mypy
uv run pytest -q
```

---

## 6. 수용 기준 (Acceptance Criteria)

- [ ] `pyproject.toml`이 4장 내용과 동일하게 생성됨.
- [ ] `.[aws]`로 설치했을 때 `ollama` / `neo4j` / `torch`가 **설치되지 않음.**
- [ ] `.[onprem]`에 `a2a-sdk`, `ollama`, `mcp`가 포함됨.
- [ ] `.[mcp-neo4j]`에 `mcp`, `neo4j`가 포함됨.
- [ ] 4개 `[project.scripts]` 엔트리포인트가 각각 스텁 `main()`으로 연결되어 `--help` 없이 즉시 종료해도 import 에러가 없음.
- [ ] `ruff check` / `mypy` / `pytest` 전부 통과.
- [ ] `tests/test_smoke.py`가 `exaone_a2a` 하위 모듈 import를 검증.

---

## 7. 범위 밖 (지금 하지 말 것)

- Vercel/Next.js 프런트엔드 (별도 `web/` 디렉터리, TypeScript).
- 실제 A2A Agent Card·스킬 정의, Ollama 호출 로직, Neo4j Cypher 쿼리 — 다음 이터레이션.
- Docker/Terraform/배포 스크립트.
- 버전 상한 핀 고정 — 하한(`>=`)만 두고 락파일(`uv.lock`)로 재현성 확보.
- Neo4j 설치/기동 — 스캐폴딩 단계에선 불필요 (RAM 상향 후 배포 문서 단계에서).
