# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

## 언어 설정

- 항상 한국어로 응답한다.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

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

## 4. Goal-Driven Execution

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

---

## 5. 프로젝트 자동 적용 규칙 (외부 문서 참조)

아래 문서의 규칙은 **사용자의 명령 없이 자동으로 적용**한다.
해당 영역의 코드를 작성·수정하기 전에 반드시 이 문서를 읽고 규칙을 따른다.

### React / Next.js 작업 시

- **참조 문서**: `docs/DevOps/Frontend/REACT_RULES.md` (프로젝트 루트 기준 상대 경로)
- **핵심 규칙**: 하나의 컴포넌트에서 `useState`가 2개 이상이면 묻지 말고 FormData 패턴 또는 단일 객체 패턴으로 자동 압축한다.
- **적용 시점**: `frontend/` 디렉토리의 `.tsx` / `.ts` / `.jsx` / `.js` 파일을 읽거나 작성·수정할 때.
- **적용 절차**:
  1. 작업 시작 전 위 문서를 먼저 읽는다.
  2. 규칙에 해당하면 자동으로 적용한다 (사용자가 "useState 유지"를 명시적으로 요청한 경우 제외).
  3. 어떤 규칙을 따랐는지 한 줄로 명시한다.
