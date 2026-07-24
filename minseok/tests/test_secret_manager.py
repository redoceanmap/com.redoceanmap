"""전역 비밀값 관리자 검증 — 개인키 경계, 1회 로드, 필수 키 실패.

핵심은 첫 두 케이스다: `.env.auth`(발급 개인키)는 자동으로 로드되지 않고,
`load_auth_env()`를 명시 호출한 프로세스에서만 보인다. 이 경계가 무너지면
백엔드 프로세스가 토큰을 발급할 수 있게 되므로 회귀를 테스트로 막는다.
"""
import os

import pytest

from core.key.secret_manager import SecretManager

_PUBLIC_NAME = "SECRET_MANAGER_TEST_PUBLIC"
_PRIVATE_NAME = "SECRET_MANAGER_TEST_PRIVATE"


@pytest.fixture
def 임시_비밀값(tmp_path):
    """공용 `.env`와 개인키 `.env.auth`를 나란히 둔 임시 디렉토리."""
    (tmp_path / ".env").write_text(f"{_PUBLIC_NAME}=공용값\n")
    (tmp_path / ".env.auth").write_text(f"{_PRIVATE_NAME}=개인키값\n")
    for name in (_PUBLIC_NAME, _PRIVATE_NAME):
        os.environ.pop(name, None)
    yield SecretManager(env_path=tmp_path / ".env")
    for name in (_PUBLIC_NAME, _PRIVATE_NAME):
        os.environ.pop(name, None)


def test_공용_env만_자동_로드되고_개인키는_보이지_않는다(임시_비밀값):
    assert 임시_비밀값.get(_PUBLIC_NAME) == "공용값"
    assert 임시_비밀값.get(_PRIVATE_NAME) == ""


def test_load_auth_env를_호출한_프로세스만_개인키를_본다(임시_비밀값):
    임시_비밀값.load_auth_env()

    assert 임시_비밀값.get(_PRIVATE_NAME) == "개인키값"
    assert 임시_비밀값.get(_PUBLIC_NAME) == "공용값"  # 공용 파일도 함께 로드된다


def test_같은_파일은_두_번_로드하지_않는다(임시_비밀값):
    임시_비밀값.load_auth_env()
    임시_비밀값.load_auth_env()
    임시_비밀값.load_env()

    assert sorted(p.name for p in 임시_비밀값._loaded) == [".env", ".env.auth"]


def test_require는_미설정_키에_즉시_실패한다(임시_비밀값):
    with pytest.raises(RuntimeError, match=_PRIVATE_NAME):
        임시_비밀값.require(_PRIVATE_NAME)


def test_이미_설정된_환경변수는_env_파일이_덮지_않는다(임시_비밀값):
    os.environ[_PUBLIC_NAME] = "컨테이너_주입값"

    assert 임시_비밀값.get(_PUBLIC_NAME) == "컨테이너_주입값"


def test_싱글톤은_프로세스당_하나다():
    assert SecretManager.instance() is SecretManager.instance()
