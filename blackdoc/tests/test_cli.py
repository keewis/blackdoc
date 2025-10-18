import textwrap
from dataclasses import dataclass

import black
import pytest

from blackdoc.__main__ import format_and_check, format_and_overwrite


@dataclass
class FormatResult:
    unformatted: str
    formatted: str
    result: str


@pytest.fixture()
def sample_code():
    unformatted = textwrap.dedent(
        """\
    >>> import a
    >>> def f(a:int=None)->str :
    ...     return  'b'
    """.rstrip()
    )

    formatted = textwrap.dedent(
        """\
    >>> import a
    >>> def f(a: int = None) -> str:
    ...     return "b"
    """.rstrip()
    )
    result = "reformatted"

    yield FormatResult(
        formatted=formatted,
        unformatted=unformatted,
        result=result,
    )


def test_format_and_overwrite(sample_code, tmp_path):
    data_path = tmp_path.joinpath("sample.py")
    data_path.write_text(sample_code.unformatted)

    mode = black.Mode(
        line_length=88,
        target_versions={black.TargetVersion["PY312"]},
        string_normalization=True,
    )

    result = format_and_overwrite(data_path, mode)
    actual = data_path.read_text()

    assert result == sample_code.result
    assert actual == sample_code.formatted


def test_format_and_check(sample_code, tmp_path, capsys):
    data_path = tmp_path.joinpath("sample.py")
    data_path.write_text(sample_code.unformatted)

    mode = black.Mode(
        line_length=88,
        target_versions={black.TargetVersion["PY312"]},
        string_normalization=True,
    )

    result = format_and_check(data_path, mode, diff=True, color=False)

    stdout, stderr = capsys.readouterr()
    print("stdout:", repr(stdout))
    print("stderr:", repr(stderr))

    assert result == sample_code.result
    assert data_path.read_text() == sample_code.unformatted
    assert stdout != ""
