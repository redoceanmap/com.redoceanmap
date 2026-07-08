# [Specification] 수신 메일 트리아지(분류·격상) 정책 — 테스트 하네스 명세

> ragwatson sherlock_homes의 Watson Watcher 정책을 redoceanmap 구조로 이식한 설계안.
> **진행 상태(2026-07-02)**: ① 유해성 1차 분류 v1 — `POST /watcher/screen`
> (KcELECTRA+Unsmile, 정책은 domain/services/moderation_policy). ② **수신 관문 연결 완료** —
> 허브 `/automation/mail` → MailStorageGateway → `watcher.screen_and_receive`:
> 유해 메일은 차단(미저장·기록), 정상 메일만 임베딩→pgvector 파이프라인으로.
> 격상(Case B — 중요/보고서 메일 오케스트레이터 라우팅)은 미구현.

## 1. System Overview & Architecture Context

본 시스템은 허브 앤 스포크(Hub-and-Spoke) 기반의 멀티 에이전트 아키텍처이다.

- **최고 사령탑 (Brain)**: `core/llm/llm_orchestrator.py`
  LLM 오케스트레이터 — EXAONE 7.8B를 기본 보유하는 단일 추론 수렴점.
- **허브 (계약·온톨로지 버스)**: `apps/hub/`
  앱 간 협력 계약(포트+DTO), 온톨로지(`hub/domain/`), 외부 자동화 창구(`/automation/*`)를 총괄.
- **커뮤니케이션 스포크**: `apps/mail/`
  외부 채널(Gmail — 향후 Telegram·Discord 확장)의 수신 이벤트를 영속화·검색하는 스포크.
- **도메인 스포크**: `apps/market/`(상권) · `apps/stock/`(주식) · `apps/chat/`(대화) 등.

## 2. Agent Core Logic & Routing Criteria

외부 채널로 인입되는 메일은 중요도·의도(Intent)에 따라 다음과 같이 라우팅한다.

- **Case A (일반 업무)**: 중요 발신자가 아니거나 단순 문의인 경우
  ➔ `mail` 스포크가 자체적으로 처리(저장 + 임베딩)하고 종결. (현재 구현 상태)
- **Case B (중요/에스컬레이션 업무)**: 중요 발신자이거나 자동 보고서 생성을 요청하는 경우
  ➔ 허브를 경유해 **LLM 오케스트레이터(EXAONE 7.8B)**로 격상(Escalation).
  오케스트레이터가 도메인 스포크(market·stock) 데이터를 취합해 보고서를 생성·회신
  (`/email/request` 발송 경로 재사용).

## 3. Watcher (Triage / Entry Point) 역할 정의

`hub`의 `/automation/mail` 뒤에 둘 **트리아지 단계**는 단순 저장이 아닌
**'Triage Nurse(초진 및 분류 관문)'** 역할을 수행한다.

### 트리아지의 핵심 메커니즘

1. **감시 및 후킹 (Watch & Hook)**: n8n(Gmail Push)으로부터 수신 메일 이벤트를 받는다.
2. **1차 분류 (Validation & Triage)**: 발신자(중요 발신자 여부)와 본문(보고서 요청 등의
   의도)을 경량 모델(EXAONE 2.4B)로 빠르게 분석 — chat phase0 의도 분류와 동일 패턴.
3. **라우팅 결정 (Routing Decision)**:
   - 일반 메일 ➔ `mail/app/use_cases`(저장·임베딩)로 종결.
   - 중요/보고서 메일 ➔ 허브 포트를 통해 오케스트레이터 격상 파이프라인 발행.

## 4. Test Harness Implementation Instructions (for Claude)

이 문서를 컨텍스트로 받는 LLM은 위 설계를 검증하는 테스트 하네스를 다음 지시로 생성한다.

### [지시사항 1] 가상 이벤트 생성기 (Mock Event Generator)

- n8n이 `/automation/mail`로 보내는 수신 이벤트를 모사하는 Mock 데이터 생성기를 작성할 것.
- 시나리오 최소 2가지:
  - **Scenario 1**: 일반 발신자의 단순 인사/문의 메일.
  - **Scenario 2**: 중요 발신자(`important_sender: true`)의 "분기 상권/주식 보고서 발행 요망" 메일.

### [지시사항 2] 트리아지 인터셉터 구현

- Mock 이벤트를 트리아지 단계가 가로채 분류하는 로직을 구현할 것.
- **일반 처리 트리거**: Scenario 1 감지 시 `mail` 유스케이스(저장·임베딩) 호출 후 로그.
- **격상 트리거**: Scenario 2 감지 시 허브 포트를 거쳐 `core/llm/llm_orchestrator.py`가
  보고서 생성을 수행하는 파이프라인을 구현할 것.

### [지시사항 3] 하네스 검증 로그

- 인입부터 처리 완료(트리아지 ➔ mail 종결 또는 트리아지 ➔ 허브 ➔ 오케스트레이터)까지
  전체 여정을 추적 서사 로그(Narrative Log)로 출력하는 모니터링을 포함할 것.
