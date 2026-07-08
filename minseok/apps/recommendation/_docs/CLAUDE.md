# CLAUDE.md — recommendation 앱

백엔드 → [[minseok/_docs/CLAUDE|minseok CLAUDE]]

상권 추천 결과를 기록·조회하는 스포크. chat이 만든 추천을 영속화하고 지도/어드민에서 재조회한다.

---

## 역할

- 추천 1건(`recommendations` 테이블) = 대화·상권·업종·사유·좌표.
- `RecommendationInteractor`(대장)가 저장/조회 유스케이스를 조립한다.
- **기록 경로**: chat → 허브 `RecommendationRecordPort` → recommendation. 스포크끼리 직접 잇지 않는다
  (교차 협력은 허브 경유 — hub CLAUDE 참고). 구현은 `RecommendationRecordGateway`가
  허브 계약 DTO를 도메인 초안으로 변환해 유스케이스에 위임하고, `main.py`가 주입한다.

## 레이어

```
apps/recommendation/
├── domain/entities/recommendation_entity.py   # Recommendation (frozen)
├── app/
│   ├── dtos/recommendation_dto.py              # RecommendationDraft
│   ├── ports/input/recommendation_use_case.py
│   ├── ports/output/recommendation_repository.py
│   └── use_cases/recommendation_interactor.py  # 대장
├── adapter/
│   ├── inbound/api/v1/recommendation_router.py # GET /recommendations[/conversation/{id}]
│   └── outbound/
│       ├── orm/recommendation_orm.py           # recommendations 테이블
│       ├── mappers/recommendation_mapper.py
│       ├── pg/recommendation_pg_repository.py
│       └── gateways/recommendation_record_gateway.py  # 허브 RecommendationRecordPort 구현
└── dependencies/recommendation_provider.py     # 유스케이스 + 기록 게이트웨이 프로바이더
```

**의존 방향:** `adapter → app → domain`. 컨벤션 → [[minseok/_docs/CLAUDE|minseok CLAUDE]].
