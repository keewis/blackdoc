import textwrap

import more_itertools
import pytest

from ..formats import rst
from .data import rst as data


@pytest.mark.parametrize(
    "lines,expected",
    (
        pytest.param(data.lines[0], None, id="none"),
        pytest.param(data.lines[2:5], None, id="no_code"),
        pytest.param(
            data.lines[8:15],
            ((1, 8), rst.name, "\n".join(data.lines[8:15])),
            id="code",
        ),
        pytest.param(
            data.lines[17:24],
            ((1, 8), rst.name, "\n".join(data.lines[17:24])),
            id="code-block",
        ),
        pytest.param(
            data.lines[27:34],
            ((1, 8), rst.name, "\n".join(data.lines[27:34])),
            id="ipython",
        ),
        pytest.param(
            data.lines[37:48],
            ((1, 12), rst.name, "\n".join(data.lines[37:48])),
            id="ipython-prompt",
        ),
    ),
)
def test_detection_func(lines, expected):
    lines = more_itertools.peekable(
        enumerate(more_itertools.always_iterable(lines), start=1)
    )

    actual = rst.detection_func(lines)
    assert actual == expected


@pytest.mark.parametrize(
    "code,expected",
    (
        pytest.param(
            textwrap.dedent("\n".join(data.lines[8:15])),
            (
                {"name": "code", "language": "python", "options": (":okwarning:",)},
                textwrap.dedent("\n".join(data.lines[11:15])),
            ),
            id="code",
        ),
        pytest.param(
            textwrap.dedent("\n".join(data.lines[17:24])),
            (
                {"name": "code-block", "language": "python", "options": ()},
                textwrap.dedent("\n".join(data.lines[19:24])),
            ),
            id="code_block",
        ),
        pytest.param(
            textwrap.dedent("\n".join(data.lines[27:34])),
            (
                {"name": "ipython", "language": None, "options": ()},
                textwrap.dedent("\n".join(data.lines[29:34])),
            ),
            id="ipython",
        ),
    ),
)
def test_extraction_func(code, expected):
    actual = rst.extraction_func(code)

    assert expected == actual


@pytest.mark.parametrize(
    "code,directive,expected",
    (
        pytest.param(
            textwrap.dedent("\n".join(data.lines[11:15])),
            {"name": "code", "language": "python", "options": (":okwarning:",)},
            textwrap.dedent("\n".join(data.lines[8:15])),
            id="code",
        ),
        pytest.param(
            textwrap.dedent("\n".join(data.lines[19:24])),
            {"name": "code-block", "language": "python", "options": ()},
            textwrap.dedent("\n".join(data.lines[17:24])),
            id="code_block",
        ),
        pytest.param(
            textwrap.dedent("\n".join(data.lines[29:34])),
            {"name": "ipython", "language": None, "options": ()},
            textwrap.dedent("\n".join(data.lines[27:34])),
            id="ipython",
        ),
    ),
)
def test_reformatting_func(code, directive, expected):
    actual = rst.reformatting_func(code, **directive)

    assert expected == actual
