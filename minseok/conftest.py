"""테스트 공용 env — 발급 테스트가 쓰는 개인키(.env.auth)를 로드한다.

배포에서 개인키는 auth 컨테이너(env_file)에만 있지만, 로컬 테스트는
발급→검증 왕복을 검증해야 하므로 auth 엔트리포인트와 같은 파일을 읽는다.
"""
from core.key.secret_manager import get_secret_manager

get_secret_manager().load_auth_env()
