import pytest

from blackdoc import autoupdate


@pytest.mark.parametrize(
    ["content", "expected"],
    (
        pytest.param(
            """\
            - repo: https://github.com/psf/black
              rev: 23.1.0
              hooks:
                - id: black
            """,
            "23.1.0",
        ),
        pytest.param(
            """\
            - repo: https://github.com/psf/black
              rev: 22.7.1
              hooks:
                - id: black-jupyter
            """,
            "22.7.1",
        ),
        pytest.param(
            """\
            - repo: https://github.com/psf/black-pre-commit-mirror
              rev: 23.10.1
              hooks:
                - id: black
            """,
            "23.10.1",
        ),
        pytest.param(
            """\
            - repo: https://github.com/psf/black-pre-commit-mirror
              rev: 22.9.10
              hooks:
                - id: black-jupyter
            """,
            "22.9.10",
        ),
        pytest.param(
            """\
            - repo: https://github.com/psf/black-pre-commit-mirror
              rev: 24.12.1
              hooks:
                - id: black
                - id: black-jupyter
            """,
            "24.12.1",
        ),
        pytest.param(
            """\
            - repo: https://github.com/psf/black-pre-commit-mirror
              rev: 24.12.1
              hooks:
                - id: black-jupyter
                - id: black
            """,
            "24.12.1",
        ),
    ),
)
def test_find_black_version(content, expected):
    version = autoupdate.find_black_version(content)

    assert version == expected
