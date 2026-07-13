# CLAUDE.md — 프로젝트 루트

[Andrej Karpathy의 관찰](https://x.com/karpathy/status/2015883857489522876)을 바탕으로 한 **에이전트 하네스**다. 에이전트의 경계·검증·스코프를 고정해 침묵 가정, 과설계, 스코프 확장, 모호한 "됐다" 선언을 줄인다. 에이전트(Claude Code, Cursor, Codex 등)는 코드·설정·명령을 제안·실행하기 전에 본 문서를 먼저 읽고, 프로젝트별 지침과 병합해 해석한다.

## 언어 설정

- 항상 한국어로 응답한다.

---

## 하위 CLAUDE.md 링크 (WikiLink)

작업 디렉토리가 아래 영역에 속하면 해당 CLAUDE.md를 **먼저 읽고** 규칙을 적용한다.
각 영역 루트의 `CLAUDE.md`는 `_docs/CLAUDE.md`로의 **심볼릭 링크**다(실내용은 `_docs/`에).

| 영역 | 문서 |
| --- | --- |
| 백엔드 (Python / FastAPI) | [[minseok/_docs/CLAUDE\|minseok CLAUDE]] |
| 프론트엔드 (Next.js) | [[www/_docs/CLAUDE\|www CLAUDE]] |
| 하네스 (구조 검증) | [[_docs/harness\|harness]] |
| 고도화 로드맵 (3단계·18 마일스톤) | [[minseok/_docs/ROADMAP\|ROADMAP]] |

> 앱은 **스타 토폴로지**(허브 `hub` + 스포크)다. 앱별 문서는 [[minseok/_docs/CLAUDE|minseok CLAUDE]]의
> 앱 표에서 잇는다. 새 앱은 `minseok/apps/<app>/_docs/CLAUDE.md` + 심볼릭 링크
> `<app>/CLAUDE.md → _docs/CLAUDE.md`를 같은 패턴으로 추가한다.

---

## 자동 적용 규칙 — 프론트엔드(www)

`www/` 디렉토리의 React/Next.js 코드(`.tsx` / `.ts` / `.jsx` / `.js`)를 읽거나 작성·수정할 때는 `www/_docs/REACT_RULES.md`를 먼저 읽고 자동 적용한다.

- **핵심 규칙:** 하나의 컴포넌트에 `useState`가 2개 이상이면 묻지 말고 FormData 패턴(폼 제출) 또는 단일 객체 패턴(실시간 상태)으로 압축한다.
- **예외:** 사용자가 명시적으로 "useState 유지"를 요청한 경우.
- **결과 보고:** 어떤 패턴을 적용했는지 한 줄로 명시한다.

---

## 공통 행동 원칙

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
