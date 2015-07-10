from spirent.methodology.results.ResultEnum import EnumVerdict


def test_verdict_summarization():
    assert EnumVerdict.do_override_verdict(EnumVerdict.none, EnumVerdict.none) is True
    assert EnumVerdict.do_override_verdict(EnumVerdict.none, EnumVerdict.passed) is True
    assert EnumVerdict.do_override_verdict(EnumVerdict.none, EnumVerdict.failed) is True

    assert EnumVerdict.do_override_verdict(EnumVerdict.passed, EnumVerdict.none) is False
    assert EnumVerdict.do_override_verdict(EnumVerdict.passed, EnumVerdict.passed) is True
    assert EnumVerdict.do_override_verdict(EnumVerdict.passed, EnumVerdict.failed) is True

    assert EnumVerdict.do_override_verdict(EnumVerdict.failed, EnumVerdict.none) is False
    assert EnumVerdict.do_override_verdict(EnumVerdict.failed, EnumVerdict.passed) is False
    assert EnumVerdict.do_override_verdict(EnumVerdict.failed, EnumVerdict.failed) is True