# ENTITY_RULES.md

백엔드 엔티티(테이블) 정의 시 자동으로 적용되는 규칙.

**ORM 스타일**: 이 프로젝트는 **SQLAlchemy 2.0 스타일** (`Mapped[...]` + `mapped_column(...)`) 로 통일한다.
SQLModel(`Field(...)`) 스타일은 사용하지 않는다.

## 1. 기본 키 (Primary Key) 규칙

**이 프로젝트의 모든 테이블은 반드시 `int` 타입의 자동 증감 고유 번호를 기본 키로 가진다. 컬럼명은 예외 없이 `id` 로 통일한다.**

### 1-1. 표준 코드 패턴

```python
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class ExampleModel(Base):
    __tablename__ = "examples"

    # 시스템 내부용 자동 증감 고유 번호 (기본 키)
    id: Mapped[int] = mapped_column(primary_key=True)
```

### 1-2. 규칙 상세

- **타입**: `Mapped[int]` — SQLAlchemy 2.0 타입 어노테이션 매핑을 사용한다.
- **컬럼 정의**: `mapped_column(primary_key=True)` — 자동 증감(autoincrement)은 정수형 단일 PK 에 대해 SQLAlchemy 가 기본 적용한다.
- **속성명**: 반드시 `id` — DB 컬럼명도 동일하게 `id` 가 된다 (별칭 금지).
- **단일 컬럼 PK**: 복합 키는 사용하지 않는다.

### 1-3. 금지 사항

- UUID, ULID, 문자열, 복합 키를 PK 로 사용하지 않는다.
- 비즈니스 식별자(`user_id`, `email`, `code` 등)를 PK 로 사용하지 않는다. 별도 유니크 컬럼으로 분리한다.

  ```python
  # ❌ 금지
  user_id: Mapped[str] = mapped_column(primary_key=True)

  # ✅ 권장
  id: Mapped[int] = mapped_column(primary_key=True)
  user_id: Mapped[str] = mapped_column(unique=True)
  ```

- `Field(...)`, `sa_column_kwargs=...` 등 SQLModel 스타일은 사용하지 않는다.

## 2. 적용 시점

- `minseok/` 디렉토리 하위의 모든 모델/엔티티 파일을 작성하거나 수정할 때.
- 새 테이블을 정의할 때, 사용자의 추가 지시 없이 위 패턴을 자동으로 적용한다.
- 기존 테이블이 규칙을 위반하고 있다면, 발견 시점에 사용자에게 알리고 마이그레이션 여부를 확인한다.
