# React 코딩 규칙 (자동 적용)

> 이 문서의 규칙은 **사용자의 명령 없이 자동으로 적용**된다.
> React/Next.js 코드를 작성하거나 수정할 때 항상 이 규칙을 먼저 검토하고 따른다.

---

## 규칙 1: useState 최소화 — 여러 상태는 하나로 압축한다

### 적용 시점 (자동 트리거)

다음 상황 중 하나라도 해당되면 **묻지 말고 자동으로 압축 패턴을 적용한다**.

- 하나의 컴포넌트에서 `useState`가 **2개 이상** 선언되어 있을 때
- 새로운 컴포넌트를 작성하면서 여러 입력값을 받아야 할 때
- 기존 `useState` 여러 개를 수정·확장할 때

### 적용 패턴

#### 패턴 A: FormData 기반 (폼 제출 흐름)

폼 제출(submit)이 목적인 입력 필드들은 `useState`를 사용하지 않는다.
대신 아래 참조 코드를 그대로 적용한다.

```tsx
const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  const formData = new FormData(e.currentTarget);
  const formProps = Object.fromEntries(formData.entries());
  // formProps.email, formProps.password 등으로 접근
};
```

- 입력 필드는 **uncontrolled component**로 처리 (`value` / `onChange` 제거)
- 각 `<input>`에 `name` 속성을 부여
- 제출 시점에 `FormData`로 일괄 수집

#### 패턴 B: 단일 useState 객체 (실시간 상태가 필요한 경우)

폼 제출이 아니라 실시간 검증·렌더링이 필요한 경우, 여러 `useState`를 하나의 객체로 합친다.

```tsx
const [state, setState] = useState({
  field1: initialValue1,
  field2: initialValue2,
});

setState(prev => ({ ...prev, field1: newValue }));
```

### 적용 우선순위

1. 폼 제출이 목적이면 → **패턴 A (FormData)** 우선
2. 실시간 검증·렌더링이 필요하면 → **패턴 B (객체 useState)**
3. 단일 값이고 실시간 반영이 필요하면 → 일반 `useState` 허용

### 적용 시 준수사항

- 비즈니스 로직, 검증 로직, API 호출은 변경하지 않는다 (Surgical Changes).
- 변환 후 사용되지 않는 import / 변수 / 핸들러는 제거한다.
- 변환 결과를 출력할 때 **어떤 패턴을 적용했는지** 한 줄로 명시한다.
- 사용자가 "useState 여러 개 유지해줘"라고 명시적으로 요청하면 이 규칙은 무시한다.
