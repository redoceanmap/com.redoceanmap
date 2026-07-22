#!/usr/bin/env bash
# JWT RS256 키쌍 생성 — 출력된 두 줄을 env 파일에 넣는다.
#   JWT_PRIVATE_KEY_B64 → .env.auth (auth 컨테이너 전용 — 발급)
#   JWT_PUBLIC_KEY_B64  → .env     (전 컨테이너 공용 — 검증)
# PEM 파일은 .gitignore(*.pem) 대상이며, env 등록 후 삭제해도 된다.
set -euo pipefail
cd "$(dirname "$0")"
openssl genrsa -out jwt_private.pem 2048
openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem
echo "JWT_PRIVATE_KEY_B64=$(base64 < jwt_private.pem | tr -d '\n')"
echo "JWT_PUBLIC_KEY_B64=$(base64 < jwt_public.pem | tr -d '\n')"
