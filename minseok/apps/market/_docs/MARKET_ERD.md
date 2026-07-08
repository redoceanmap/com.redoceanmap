# MARKET_ERD — 서울 상권 3NF 스키마

market CLAUDE → [[minseok/apps/market/_docs/CLAUDE|market CLAUDE]]

서울시 상권분석서비스 CSV를 발자국 ERD 컨벤션으로 정규화한 스키마. 차원 5 + 팩트 8.

---

## 정규화 배경

원본(denormalized) 팩트들은 `상권_코드_명·상권_구분_코드_명·자치구·서비스_업종_코드_명`을
매 테이블에 중복 보유했다(`상권_코드 → 상권명` 이행 종속 = 3NF 위반). 차원을 추출해 이행 종속을
제거했다. 분해 컬럼(연령대·시간대·요일별)은 각각 PK에만 종속인 원자 속성이므로 넓게 유지한다
(행 분리는 과정규화).

## 차원 (5)

| 테이블 | 키 | 비고 |
|--------|-----|------|
| `region` | `code` PK | 자치구(level1) → 행정동(level2) **자기참조** `parent_code` |
| `trade_area_division` | `code` PK | A 골목 / D 발달 / R 전통시장 / U 관광특구 |
| `service_category` | `code` PK | 서비스 업종(예: CS100010 → 커피-음료). 평면 |
| `change_indicator` | `code` PK | HH 정체 / LL 다이나믹 / LH 상권확장 / HL 상권축소 |
| `trade_area` | `code`(상권_코드) PK | 중심 차원. `division_code` FK, `region_code`(행정동) FK, x/y 좌표, `lat`/`lng` property |

## 팩트 (8)

공통 `MarketStatMixin`: `id`(대리키) + `year_quarter` + `trdar_code`(FK → `trade_area.code`).
측정 컬럼만 보유하고 차원 속성은 갖지 않는다.

| 테이블 | 추가 FK | 유니크 |
|--------|--------|--------|
| `estimated_sales` | `service_code` → service_category | (year_quarter, trdar_code, service_code) |
| `store` | `service_code` → service_category | (year_quarter, trdar_code, service_code) |
| `floating_population` | — | (year_quarter, trdar_code) |
| `resident_population` | — | (year_quarter, trdar_code) |
| `working_population` | — | (year_quarter, trdar_code) |
| `consumption` | — | (year_quarter, trdar_code) |
| `apartment` | — | (year_quarter, trdar_code) |
| `commercial_change` | `change_indicator` → change_indicator | (year_quarter, trdar_code) |

## 조인 관계

```
fact ──trdar_code──▶ trade_area ──division_code──▶ trade_area_division
                          │
                          └─region_code──▶ region(행정동) ──parent_code──▶ region(자치구)
estimated_sales/store ──service_code──▶ service_category
commercial_change ──change_indicator──▶ change_indicator
```

## 적재

`scripts/ingest_seoul_3nf.py`가 차원 먼저 → 팩트(FK 무결성 필터) 순으로 적재.
매핑은 `adapter/outbound/csv/column_maps.py`. 조회 경로 → [[minseok/apps/market/_docs/CLAUDE|market CLAUDE]].
