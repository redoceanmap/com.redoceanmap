# CLAUDE.md — market 앱

백엔드 → [[minseok/_docs/CLAUDE|minseok CLAUDE]]

서울 상권 분석 도메인 스포크. 상권 데이터(3NF)를 소유하고, 허브 포트 구현으로 chat에 제공한다.

---

## 문서

| 문서 | 내용 |
|------|------|
| [[minseok/apps/market/_docs/MARKET_ERD|MARKET_ERD]] | 3NF 스키마 — 차원 5 + 팩트 8, FK, 정규화 이력 |

---

## 데이터 스키마 — 3NF

발자국 ERD 컨벤션을 적용한 정규화 스키마. 상세 → [[minseok/apps/market/_docs/MARKET_ERD|MARKET_ERD]].

- **차원(5)**: `region`(자치구→행정동 자기참조), `trade_area_division`, `service_category`,
  `change_indicator`, `trade_area`(중심).
- **팩트(8)**: `estimated_sales`·`store`(+service FK)·`floating/resident/working_population`·
  `consumption`·`apartment`·`commercial_change`. 공통 `MarketStatMixin` = `id + year_quarter +
  trdar_code(FK→trade_area)`. 차원 속성(상권명·구분·지역명)은 차원 테이블로 정규화됨.
- 분해 컬럼(연령/시간/요일)은 넓게 유지 — 3NF 준수, 과정규화 회피.

## 적재 — 독립 스크립트

- `scripts/ingest_seoul_3nf.py` — CSV(`data/raw/seoul/`, cp949)를 차원 먼저 → 팩트(FK 무결성 필터)로 적재.
- CSV→ORM 매핑은 `adapter/outbound/csv/column_maps.py`(스크립트 전용).
- 개별 `/admin/ingest/*` 라우터는 제거됨(스크립트로 대체).

## 조회

| 경로 | 구현 |
|------|------|
| chat(허브 포트) | `adapter/outbound/gateways/commercial_data_gateway.py` — `CommercialDataPort` 구현. 정규화 조인으로 원시 DTO 반환. → hub CLAUDE |
| 프론트 `/market/areas` | `area` 조회 슬라이스 — `trade_area` + region 조인으로 `Area` 엔티티 반환 |

팩트 8개의 개별 조회 슬라이스(라우터·인터랙터·리포지토리·매퍼·엔티티)는 제거됨 —
런타임 조회는 위 두 경로로 수렴한다. 팩트 ORM은 게이트웨이·적재 스크립트·마이그레이션이 사용하므로 유지.

## 좌표

`utils/coords.py`의 `tm_to_wgs84`(EPSG:5174→4326)가 TM 좌표를 위경도로 변환한다.
`trade_area`·`Coordinate` VO가 `lat`/`lng` property로 노출한다.

---

## 남은 조회 슬라이스 컨벤션 (area)

로직(VO·계산)이 있는 기능에만 entity/vo/mapper를 둔다. `area`는 `Coordinate` VO가 좌표 변환을
소유하므로 `area_entity` + `area_mapper`를 둔다. 파일명은 도메인어(`area`, `trade_area` …)를 쓴다.
전체 수직 슬라이스 네이밍 → [[minseok/_docs/CLAUDE|minseok CLAUDE]].
