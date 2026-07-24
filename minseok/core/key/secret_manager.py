"""시스템 전역 비밀값(루트 `.env`)을 한곳에서 관리합니다.

프로젝트의 모든 `.env` 로드는 이 모듈을 통과합니다 — 앱 런타임(`core/config.py`),
스크립트(`scripts/*.py`), 마이그레이션(`alembic/env.py`), 테스트(`conftest.py`).
개별 모듈은 `load_dotenv`를 직접 부르지 않습니다.

관리 대상 파일은 둘입니다:

- **루트 `.env`** — 전 프로세스 공용. 최초 조회 시점에 자동 로드(1회).
- **루트 `.env.auth`** — 토큰 발급용 개인키(`JWT_PRIVATE_KEY_B64`) 전용. 자동 로드하지
  **않고**, `load_auth_env()`를 명시 호출한 프로세스(auth 엔트리포인트·테스트)만 봅니다.
  백엔드 프로세스가 개인키를 갖지 않는 기존 경계를 그대로 유지하기 위함입니다.

이미 `os.environ`에 있는 값은 덮어쓰지 않습니다(`load_dotenv` 기본 `override=False`) —
컨테이너의 `env_file`·`environment` 주입이 파일보다 우선합니다.
"""

from __future__ import annotations

import os
from pathlib import Path

_AUTH_ENV_FILENAME = ".env.auth"

# core/config.py가 노출하는 GEMINI_MODEL의 기본값 — 정의처는 여기 한 곳뿐이다.
_DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite"


def default_env_path() -> Path:
    """프로젝트 루트 `.env` — 이 파일: `minseok/core/key/secret_manager.py` 기준."""
    return Path(__file__).resolve().parents[3] / ".env"


def auth_env_path() -> Path:
    """프로젝트 루트 `.env.auth` — 토큰 발급 개인키 전용."""
    return default_env_path().with_name(_AUTH_ENV_FILENAME)


class SecretManager:
    """전역 비밀값 관리자 (프로세스당 하나).

    - 파일별로 한 번만 로드(`load_env` / `load_auth_env`)
    - 이름으로 조회(`get`) / 없으면 실패(`require`)
    - Gemini 키·모델명 접근자 (클라이언트 객체는 보관하지 않는다 — 이 프로젝트의
      Gemini 호출은 `hub`의 REST 어댑터가 담당)
    """

    _instance: SecretManager | None = None

    def __init__(self, env_path: Path | None = None) -> None:
        self._env_path = env_path or default_env_path()
        self._loaded: set[Path] = set()

    @classmethod
    def instance(cls, env_path: Path | None = None) -> SecretManager:
        """프로세스당 하나의 SecretManager (첫 생성 시 env_path만 적용)."""
        if cls._instance is None:
            cls._instance = cls(env_path=env_path)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """테스트 등에서 인스턴스를 비울 때만 사용(이미 로드된 os.environ은 되돌리지 않는다)."""
        cls._instance = None

    def _load_file(self, path: Path) -> None:
        if path in self._loaded:
            return
        from dotenv import load_dotenv

        load_dotenv(path)
        self._loaded.add(path)

    def load_env(self) -> None:
        """공용 `.env`를 한 번만 로드합니다."""
        self._load_file(self._env_path)

    def load_auth_env(self) -> None:
        """발급 개인키가 필요한 프로세스만 호출합니다 — `.env.auth`를 추가로 로드."""
        self.load_env()
        self._load_file(self._env_path.with_name(_AUTH_ENV_FILENAME))

    def get(self, name: str, default: str = "") -> str:
        """환경 변수 조회. 필요 시 `.env` 로드를 트리거합니다."""
        self.load_env()
        return (os.getenv(name) or default).strip()

    def require(self, name: str) -> str:
        """필수 비밀값 — 비어 있으면 즉시 실패(설정 누락을 런타임 깊은 곳까지 끌고 가지 않는다)."""
        value = self.get(name)
        if not value:
            raise RuntimeError(f"{name} 미설정 — 루트 .env를 확인하세요 ({self._env_path})")
        return value

    def get_gemini_api_key(self) -> str:
        return self.get("GEMINI_API_KEY")

    def get_gemini_model_name(self) -> str:
        return self.get("GEMINI_MODEL", _DEFAULT_GEMINI_MODEL)

    def is_gemini_ready(self) -> bool:
        return bool(self.get_gemini_api_key())


def get_secret_manager(env_path: Path | None = None) -> SecretManager:
    """애플리케이션 전역에서 사용할 SecretManager 싱글톤."""
    return SecretManager.instance(env_path=env_path)
