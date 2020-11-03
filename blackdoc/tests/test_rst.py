import textwrap

import more_itertools
import pytest

from .. import blacken
from ..formats import rst
from .data import rst as data


@pytest.mark.parametrize(
    "lines,expected",
    (
        pytest.param(data.lines[0], None, id="none"),
        pytest.param(data.lines[2:5], None, id="no_code"),
        pytest.param(data.lines[67:70], None, id="code_other_language"),
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
        pytest.param(data.lines[38:47], None, id="ipython-prompt"),
        pytest.param(data.lines[52:64], None, id="ipython-prompt-cell-decorator"),
        pytest.param(
            data.lines[73:79],
            ((1, 7), rst.name, "\n".join(data.lines[73:79])),
            id="testsetup",
        ),
        pytest.param(
            data.lines[80:83],
            ((1, 4), rst.name, "\n".join(data.lines[80:83])),
            id="testcode",
        ),
        pytest.param(
            data.lines[84:87],
            ((1, 4), rst.name, "\n".join(data.lines[84:87])),
            id="testcleanup",
        ),
    ),
)
def test_detection_func(lines, expected):
    lines = tuple(more_itertools.always_iterable(lines))
    lines_ = more_itertools.peekable(enumerate(lines, start=1))

    actual = rst.detection_func(lines_)

    leftover_lines = tuple(lines_)

    assert actual == expected
    assert expected is not None or len(lines) == len(leftover_lines)


@pytest.mark.parametrize(
    "code,expected",
    (
        pytest.param(
            textwrap.dedent("\n".join(data.lines[8:15])),
            (
                {
                    "name": "code",
                    "language": "python",
                    "options": (":okwarning:",),
                    "prompt_length": 3,
                    "n_header_lines": 3,
                },
                textwrap.dedent("\n".join(data.lines[11:15])),
            ),
            id="code",
        ),
        pytest.param(
            textwrap.dedent("\n".join(data.lines[17:24])),
            (
                {
                    "name": "code-block",
                    "language": "python",
                    "options": (),
                    "prompt_length": 4,
                    "n_header_lines": 2,
                },
                textwrap.dedent("\n".join(data.lines[19:24])),
            ),
            id="code_block",
        ),
        pytest.param(
            textwrap.dedent("\n".join(data.lines[27:34])),
            (
                {
                    "name": "ipython",
                    "language": None,
                    "options": (),
                    "prompt_length": 4,
                    "n_header_lines": 2,
                },
                rst.hide_magic(textwrap.dedent("\n".join(data.lines[29:34]))),
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
            {
                "name": "code",
                "language": "python",
                "options": (":okwarning:",),
                "prompt_length": 3,
            },
            textwrap.dedent("\n".join(data.lines[8:15])),
            id="code",
        ),
        pytest.param(
            textwrap.dedent("\n".join(data.lines[19:24])),
            {
                "name": "code-block",
                "language": "python",
                "options": (),
                "prompt_length": 4,
            },
            textwrap.dedent("\n".join(data.lines[17:24])),
            id="code_block",
        ),
        pytest.param(
            textwrap.dedent("\n".join(data.lines[29:34])),
            {"name": "ipython", "language": None, "options": (), "prompt_length": 4},
            textwrap.dedent("\n".join(data.lines[27:34])),
            id="ipython",
        ),
    ),
)
def test_reformatting_func(code, directive, expected):
    actual = rst.reformatting_func(code, **directive)

    assert expected == actual


def test_blacken():
    labeled = tuple(
        ((min_ + 1, max_ + 1), label, "\n".join(data.lines[slice(min_, max_)]))
        for label, (min_, max_) in zip(data.line_labels, data.line_ranges)
    )
    actual = tuple(blacken(labeled))

    assert len("\n".join(actual).split("\n")) == 75
