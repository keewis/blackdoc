import blackdoc


def test_version():
    assert getattr(blackdoc, "__version__", "") not in ("", "999")
