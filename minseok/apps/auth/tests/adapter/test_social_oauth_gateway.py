from auth.adapter.outbound.gateways.social_oauth_gateway import SocialOauthGateway


def _term(tag: str, agreed: bool) -> dict:
    return {"tag": tag, "agreed": agreed, "required": tag != "marketing"}


def test_필수_태그_3종이_전부_동의되면_카카오_화면_동의로_인정한다():
    terms = [_term("age", True), _term("terms", True), _term("privacy", True)]
    assert SocialOauthGateway._parse_kakao_terms(terms) == (True, False)


def test_만14세_태그가_콘솔에_누락되면_자체_동의_페이지로_폴백한다():
    terms = [_term("terms", True), _term("privacy", True)]  # age 미등록 — 동의 범위 부족
    assert SocialOauthGateway._parse_kakao_terms(terms) == (False, False)


def test_마케팅_태그_동의는_선택으로_함께_해석된다():
    terms = [
        _term("age", True),
        _term("terms", True),
        _term("privacy", True),
        _term("marketing", True),
    ]
    assert SocialOauthGateway._parse_kakao_terms(terms) == (True, True)


def test_약관이_비어_있으면_간편가입_미설정으로_보고_폴백한다():
    assert SocialOauthGateway._parse_kakao_terms([]) == (False, False)
