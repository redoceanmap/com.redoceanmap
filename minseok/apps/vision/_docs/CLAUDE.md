# CLAUDE.md — vision (스포크)

공통 규칙 → [[minseok/_docs/CLAUDE|minseok CLAUDE]] · YOLO 배경 지식 → [[minseok/apps/vision/_docs/YOLO_RESEARCH|YOLO_RESEARCH]]

비전 처리(이미지 분석) 스포크 앱. 헥사고날 레이어(`adapter → app → domain`)를 따르며,
다른 스포크와의 협력은 허브(`apps/hub`)를 경유한다.

YOLO 관련 코드(얼굴 탐지 파인튜닝 `FaceTrainingInteractor`, `resources/yolo_train` 데이터셋)를
읽거나 수정할 때는 [[minseok/apps/vision/_docs/YOLO_RESEARCH|YOLO_RESEARCH]]를 먼저 읽는다.

## 구조

```
vision/
├── domain/                            # 순수 도메인 — 외부 의존 금지
├── app/
│   ├── ports/{input,output}/          # UseCase / Repository ABC
│   ├── use_cases/                     # Interactor
│   └── dtos/                          # 레이어 간 전달 객체
├── adapter/
│   ├── inbound/api/{schemas,v1}/      # Pydantic 스키마 · FastAPI 라우터
│   └── outbound/
├── dependencies/                      # FastAPI DI 프로바이더
└── tests/{domain,app/use_cases}/
```
