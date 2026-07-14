import json
import logging
import os
import sys
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps"))

from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from auth.adapter.inbound.api.v1.auth_router import auth_router
from chat.adapter.inbound.api.v1.chat_router import chat_router
from core.database import dispose_engine, init_engine
from core.security import get_current_user_id
from chat.adapter.outbound.gateways.email_composer_gateway import EmailComposerN8nGateway
from hub.adapter.inbound.api.v1.automation_router import automation_router
from hub.adapter.inbound.api.v1.email_request_router import email_request_router
from hub.dependencies.automation_provider import (
    get_fundamental_storage_port,
    get_mail_storage_port,
    get_news_label_storage_port,
    get_news_storage_port,
    get_price_bar_storage_port,
)
from hub.dependencies.email_request_provider import get_email_composer
from mail.adapter.inbound.api.v1.judge_router import judge_router
from mail.adapter.inbound.api.v1.mail_router import mail_router
from mail.adapter.inbound.api.v1.watcher_router import watcher_router
from mail.dependencies.watcher_provider import get_mail_storage_gateway
from hub.dependencies.commercial_data_provider import get_commercial_data_port
from hub.dependencies.news_search_provider import get_news_search_port
from hub.dependencies.recommendation_record_provider import get_recommendation_record_port
from hub.dependencies.stock_analysis_provider import get_stock_analysis_port
from market.dependencies.commercial_data_provider import get_commercial_data_gateway
from market.adapter.inbound.api.v1.area_router import area_router
from stock.adapter.inbound.api.v1.stock_router import stock_router
from stock.dependencies.stock_provider import (
    get_fundamental_storage_gateway,
    get_news_label_storage_gateway,
    get_news_search_gateway,
    get_news_storage_gateway,
    get_price_bar_storage_gateway,
    get_stock_analysis_gateway,
)
from recommendation.adapter.inbound.api.v1.recommendation_router import recommendation_router
from recommendation.dependencies.recommendation_provider import get_recommendation_record_gateway
from hub.adapter.inbound.api.v1.vision_router import vision_router

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_engine()
    try:
        yield
    finally:
        await dispose_engine()


app = FastAPI(title="redoceanmap API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 인증 가드 — 공개 화이트리스트 방식: auth(자체 처리)·automation(웹훅 토큰)·/·/health만 공개,
# 나머지 라우터는 전부 JWT 필수(core/security — 스포크는 auth를 모른다).
_authenticated = [Depends(get_current_user_id)]

app.include_router(auth_router)  # 공개 — register/login/refresh, me는 자체 검증
app.include_router(automation_router)  # 공개 — 외부 자동화 창구, X-Webhook-Token 자체 검증
app.include_router(chat_router, dependencies=_authenticated)
app.include_router(area_router, dependencies=_authenticated)
app.include_router(stock_router, dependencies=_authenticated)
app.include_router(recommendation_router, dependencies=_authenticated)
app.include_router(email_request_router, dependencies=_authenticated)  # 허브 — 이메일 발송 요청
app.include_router(mail_router, dependencies=_authenticated)
app.include_router(watcher_router, dependencies=_authenticated)
app.include_router(judge_router, dependencies=_authenticated)
app.include_router(vision_router, dependencies=_authenticated)

# 합성 루트: 허브(hub)의 포트들을 스포크 구현으로 주입한다.
# (허브는 스포크를 모르고, main.py만 둘을 안다 — 스타 토폴로지 허브 격리 유지)
app.dependency_overrides[get_commercial_data_port] = get_commercial_data_gateway
app.dependency_overrides[get_recommendation_record_port] = get_recommendation_record_gateway
app.dependency_overrides[get_stock_analysis_port] = get_stock_analysis_gateway
app.dependency_overrides[get_news_storage_port] = get_news_storage_gateway
app.dependency_overrides[get_price_bar_storage_port] = get_price_bar_storage_gateway
app.dependency_overrides[get_news_label_storage_port] = get_news_label_storage_gateway
app.dependency_overrides[get_fundamental_storage_port] = get_fundamental_storage_gateway
app.dependency_overrides[get_news_search_port] = get_news_search_gateway
app.dependency_overrides[get_email_composer] = lambda: EmailComposerN8nGateway()
app.dependency_overrides[get_mail_storage_port] = get_mail_storage_gateway


@app.get("/")
def read_root():
    content = {"message": "redoceanmap API", "docs": "/docs"}
    return Response(
        content=json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8"),
        media_type="application/json; charset=utf-8",
    )


@app.get("/health")
def health():
    return {"status": "ok"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
