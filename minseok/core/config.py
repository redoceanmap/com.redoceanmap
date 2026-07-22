import base64
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[2] / ".env")

DATABASE_URL = os.environ["DATABASE_URL"].replace(
    "postgresql://", "postgresql+psycopg://"
)

# market 전용 DB(market-pgvector, :5434) — 앱별 DB 불가침 원칙의 첫 사례.
# 미설정이면 메인 DB 폴백: 미구축 환경(맥 등)이 그대로 동작하고,
# 코드 배포와 데이터 컷오버(env 주입 + 재기동)를 분리할 수 있다.
MARKET_DATABASE_URL = os.getenv("MARKET_DATABASE_URL", os.environ["DATABASE_URL"]).replace(
    "postgresql://", "postgresql+psycopg://"
)

# JWT RS256 검증용 공개키 — 전 컨테이너 공용. 없으면 기동 실패가 맞다.
# (멀티라인 PEM은 env로 다루기 어려워 base64 단일 라인으로 주입한다 — scripts/generate_jwt_keys.sh)
JWT_PUBLIC_KEY = base64.b64decode(os.environ["JWT_PUBLIC_KEY_B64"]).decode()


def jwt_private_key() -> str:
    """RS256 발급용 개인키 — auth 컨테이너 전용.

    반드시 호출 시점에 읽는다: backend 컨테이너는 이 env 없이도
    모듈 import·기동이 되어야 한다(발급 불가는 env 부재로 강제).
    """
    raw = os.environ.get("JWT_PRIVATE_KEY_B64")
    if raw is None:
        raise RuntimeError("JWT_PRIVATE_KEY_B64 미설정 — 토큰 발급은 auth 컨테이너에서만 가능합니다.")
    return base64.b64decode(raw).decode()

# 실행 환경 — 쿠키 Secure 속성 분기(bff-cloudflared-harness 규칙 2)에만 사용.
ENV = os.getenv("ENV", "development")

# BFF 쿠키 도메인 — prod `.redoceanmap.com`(auth 서브도메인 발급 쿠키를 apex와 공유),
# dev 미설정 = host-only. Secure·Domain만 ENV 분기, 나머지 속성은 리터럴(규칙 2).
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", "")

# OAuth redirect_uri 조립 기준 — prod https://auth.redoceanmap.com/auth (이중문 직행),
# dev http://localhost:3000/api/backend/auth (프록시 경로 — 서브도메인 없음).
AUTH_CALLBACK_BASE = os.getenv("AUTH_CALLBACK_BASE", "http://localhost:3000/api/backend/auth")

# API 문서(/docs·/redoc·/openapi.json) 보호 — HTTP Basic. 미설정 시 문서 접근 전면 차단.
DOCS_USER = os.getenv("DOCS_USER", "")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "")

# 리프레시 토큰 저장소 (auth) — 컨테이너는 redis://redis:6379/0 로 덮어쓴다.
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

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

# 비전 / ConvNeXt 이미지 분류 (hub — 신뢰도 게이팅 임계값).
CONVNEXT_DEVICE = os.getenv("CONVNEXT_DEVICE", "auto")  # "auto" | "cuda" | "cpu"
CONVNEXT_HIGH_CONFIDENCE = float(os.getenv("CONVNEXT_HIGH_CONFIDENCE", "0.85"))  # 이상이면 자동 확정
CONVNEXT_LOW_CONFIDENCE = float(os.getenv("CONVNEXT_LOW_CONFIDENCE", "0.55"))  # 미만이면 사람 확인
CONVNEXT_TOP_K = int(os.getenv("CONVNEXT_TOP_K", "5"))

# Google Gemini API (허브 gemini 슬라이스 — 외부 LLM 답변). 비어 있으면 호출 시 계약 예외.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

# 소셜 로그인 OAuth (auth social 슬라이스). 비어 있으면 해당 프로바이더 로그인 시 401.
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID", "")  # 카카오 REST API 키
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET", "")  # 콘솔에서 선택 사항
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")
