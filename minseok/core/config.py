import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[2] / ".env")

DATABASE_URL = os.environ["DATABASE_URL"].replace(
    "postgresql://", "postgresql+psycopg://"
)

# JWT 서명 비밀키 — 발급(auth 인터랙터)과 검증(core/security)이 공유한다.
JWT_SECRET = os.environ["JWT_SECRET"]

# n8n → 백엔드 인바운드 웹훅 검증 토큰. 비어 있으면 검증 생략(로컬 개발).
N8N_INBOUND_TOKEN = os.getenv("N8N_INBOUND_TOKEN", "")

# 백엔드 → n8n 이메일 발송 웹훅 (Gmail 자격증명은 n8n이 보유).
N8N_EMAIL_WEBHOOK_URL = os.getenv(
    "N8N_EMAIL_WEBHOOK_URL", "http://localhost:5678/webhook/redocean-email"
)
N8N_OUTBOUND_TOKEN = os.getenv("N8N_OUTBOUND_TOKEN", "")

# vision 업로드 이미지를 저장할 S3 버킷 (자격 증명은 boto3 기본 체인 — .env의 AWS_* 키).
VISION_S3_BUCKET = os.getenv("VISION_S3_BUCKET", "")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")

# Google Gemini API (허브 gemini 슬라이스 — 외부 LLM 답변). 비어 있으면 호출 시 계약 예외.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
