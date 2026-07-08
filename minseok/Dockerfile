FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# 컨테이너(리눅스)엔 NVIDIA GPU가 없으므로 CPU 전용 torch/torchvision을 먼저 깔아 CUDA 의존성(~3.5GB) 유입을 차단
# (torchvision을 PyPI CUDA 빌드로 받으면 torch+cpu와 어긋나 torchvision::nms 연산자 등록이 실패한다)
RUN pip install --no-cache-dir torch==2.12.1+cpu torchvision==0.27.1+cpu --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt
# 컨테이너엔 디스플레이가 없으므로 GUI 시스템 라이브러리(libxcb 등)를 요구하는 opencv를 headless로 교체
RUN pip uninstall -y opencv-python && pip install --no-cache-dir opencv-python-headless==5.0.0.93

COPY . .

CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
