# 하네스(Harness) — 구조 무결성

> 카파시式 하네스 엔지니어링: 코드·문서 구조가 올바르게 유지되도록 정적 분석·제약을
> 배선(harness)처럼 엮어 자동으로 검증한다. 사람 리뷰가 놓치는 구조 위반을 실패로 만든다.

이 저장소는 두 개의 직교하는 구조를 가진다.

- **코드** — 모듈러 모놀리식 + 스타 토폴로지: `hub`(허브) 중심, 나머지 앱은 스포크.
  앱 내부는 클린 아키텍처(`adapter → app → domain`).
- **문서** — 심볼릭 링크 + Obsidian WikiLink로 엮인 지식 그래프.

---

## 1. import-linter — 코드 아키텍처 하네스

`minseok/.importlinter`가 세 계약을 강제한다.

1. **클린 아키텍처** — 모든 스포크에서 `adapter > app > domain` (역방향 import 금지)
2. **스포크 독립** — 스포크끼리 직접 import 금지 (교차 협력은 허브 경유)
3. **허브 격리** — `hub`(허브)는 스포크를 import 하지 않음

```bash
cd minseok && PYTHONPATH=apps lint-imports
```

`PYTHONPATH=apps`는 `main.py`의 `sys.path.insert`와 같은 맥락 — 앱을 최상위 패키지
(`hub`, `market`, `chat` …)로 인식시키기 위함. 스타 토폴로지 상세 → [[minseok/_docs/CLAUDE|minseok CLAUDE]].

## 2. 문서 온톨로지 — 심볼릭 + WikiLink

- 각 영역 루트의 `CLAUDE.md`는 `_docs/CLAUDE.md`로의 **심볼릭 링크**다
  (`minseok/`, `www/`, 각 앱). 실내용과 부속 규칙 문서는 `_docs/`에 둔다.
- 문서 간 연결은 Obsidian `[[경로|별칭]]` WikiLink로 한다. basename 충돌
  (`CLAUDE.md` 다수)을 피하려 하위 문서는 전체 경로 형태로 링크한다.
- 새 `.md`는 [[CLAUDE|루트 CLAUDE]]의 "문서 배치 규칙"대로 영역별 `_docs/`에 둔다.

---

## 문서 지도

| 영역 | 문서 |
|------|------|
| 루트 하네스(정본) | [[CLAUDE|CLAUDE (루트)]] |
| 백엔드 | [[minseok/_docs/CLAUDE|minseok CLAUDE]] |
| 프론트엔드 | [[www/_docs/CLAUDE|www CLAUDE]] |

앱별 문서는 [[minseok/_docs/CLAUDE|minseok CLAUDE]]의 앱 표에서 잇는다.
