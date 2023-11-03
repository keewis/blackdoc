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


@pytest.mark.parametrize(
    ["content", "version", "expected"],
    (
        pytest.param(
            """\
            - repo: https://github.com/pre-commit/pre-commit-hooks
              rev: 4.4.0
              hooks:
                - id: trailing-whitespace
                - id: end-of-file-fixer

            - repo: https://github.com/keewis/blackdoc
              rev: 3.8.0
              hooks:
                - id: blackdoc
                  additional_dependencies: ["black==22.10.0"]
                - id: blackdoc-autoupdate-black
            """,
            "23.3.0",
            """\
            - repo: https://github.com/pre-commit/pre-commit-hooks
              rev: 4.4.0
              hooks:
                - id: trailing-whitespace
                - id: end-of-file-fixer

            - repo: https://github.com/keewis/blackdoc
              rev: 3.8.0
              hooks:
                - id: blackdoc
                  additional_dependencies: ["black==23.3.0"]
                - id: blackdoc-autoupdate-black
            """,
        ),
        pytest.param(
            """\
            - repo: https://github.com/keewis/blackdoc
              rev: 3.8.0
              hooks:
                - id: blackdoc
                  additional_dependencies: ["black==22.10.0"]
                - id: blackdoc-autoupdate-black
            """,
            "21.5.1",
            """\
            - repo: https://github.com/keewis/blackdoc
              rev: 3.8.0
              hooks:
                - id: blackdoc
                  additional_dependencies: ["black==21.5.1"]
                - id: blackdoc-autoupdate-black
            """,
        ),
        pytest.param(
            """\
            - repo: https://github.com/keewis/blackdoc
              rev: 3.8.0
              hooks:
                - id: blackdoc
                  additional_dependencies: ["black==22.10.0"]
                - id: blackdoc-autoupdate-black
            """,
            "23.7.12",
            """\
            - repo: https://github.com/keewis/blackdoc
              rev: 3.8.0
              hooks:
                - id: blackdoc
                  additional_dependencies: ["black==23.7.12"]
                - id: blackdoc-autoupdate-black
            """,
        ),
    ),
)
def test_update_black_pin(content, version, expected):
    updated = autoupdate.update_black_pin(content, version)

    assert updated == expected


@pytest.mark.parametrize(
    ["content", "expected"],
    (
        pytest.param(
            """\
        hooks:
        - repo: https://github.com/psf/black
          rev: 22.0.1
          hooks:
          - id: black

        - repo: https://github.com/keewis/blackdoc
          rev: 3.9.0
          hooks:
            - id: blackdoc
              additional_dependencies: ["black==22.0.1"]
        """,
            """\
        hooks:
        - repo: https://github.com/psf/black
          rev: 22.0.1
          hooks:
          - id: black

        - repo: https://github.com/keewis/blackdoc
          rev: 3.9.0
          hooks:
            - id: blackdoc
              additional_dependencies: ["black==22.0.1"]
        """,
        ),
        pytest.param(
            """\
        hooks:
        - repo: https://github.com/psf/black
          rev: 23.10.0
          hooks:
          - id: black

        - repo: https://github.com/keewis/blackdoc
          rev: 3.9.0
          hooks:
            - id: blackdoc
              additional_dependencies: ["black==22.0.1"]
        """,
            """\
        hooks:
        - repo: https://github.com/psf/black
          rev: 23.10.0
          hooks:
          - id: black

        - repo: https://github.com/keewis/blackdoc
          rev: 3.9.0
          hooks:
            - id: blackdoc
              additional_dependencies: ["black==23.10.0"]
        """,
        ),
    ),
)
def test_main(tmp_path, content, expected):
    path = tmp_path.joinpath(".pre-commit-config.yaml")
    path.write_text(content)

    stat = path.stat()

    return_value = autoupdate.main(path)

    updated = path.read_text()

    assert updated == expected
    if content == expected:
        assert path.stat() == stat
        assert return_value == 0
    else:
        assert return_value == 1
