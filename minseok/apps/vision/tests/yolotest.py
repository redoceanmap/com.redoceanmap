"""YOLO 헬로 월드 — 샘플 이미지를 탐지하고 결과 창을 띄운다.

실행: venv/bin/python3 minseok/apps/vision/tests/yolotest.py
(pytest 대상이 아닌 단독 실행 스크립트)
"""
from ultralytics import YOLO

model = YOLO("yolov8n.pt")  # 최초 실행 시 자동 다운로드 (~6MB)
results = model("https://ultralytics.com/images/bus.jpg")  # 샘플 이미지 추론

r = results[0]
print(f"탐지 {len(r.boxes)}개:", [model.names[int(c)] for c in r.boxes.cls])
r.show()  # 바운딩 박스가 그려진 결과 이미지를 화면에 표시
