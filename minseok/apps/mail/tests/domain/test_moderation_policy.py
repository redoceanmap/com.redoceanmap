from mail.domain.services.moderation_policy import judge


def test_임계값을_넘는_유해_카테고리가_있으면_유해_판정():
    verdict = judge({"악플/욕설": 0.97, "여성/가족": 0.6, "clean": 0.02, "남성": 0.1})
    assert verdict.is_abusive is True
    assert verdict.categories == ("악플/욕설", "여성/가족")  # 점수 내림차순


def test_clean_점수는_유해_판정에_쓰이지_않는다():
    verdict = judge({"clean": 0.99, "악플/욕설": 0.1})
    assert verdict.is_abusive is False
    assert verdict.categories == ()
