import textwrap

import more_itertools
import pytest

from blackdoc.formats import doctest

from .data.doctest import lines


@pytest.mark.parametrize(
    "lines,expected",
    (
        pytest.param(lines[0], None, id="no_line"),
        pytest.param(lines[8], ((1, 2), doctest.name, lines[8]), id="single_line"),
        pytest.param(
            lines[4:8],
            ((1, 5), doctest.name, "\n".join(lines[4:8])),
            id="multiple_lines",
        ),
        pytest.param(
            lines[23], ((1, 2), doctest.name, lines[23]), id="single empty line"
        ),
        pytest.param(
            lines[17:23],
            ((1, 7), doctest.name, "\n".join(lines[17:23])),
            id="multiple lines with empty continuation line",
        ),
    ),
)
def test_detection_func(lines, expected):
    lines = more_itertools.peekable(
        enumerate(more_itertools.always_iterable(lines), start=1)
    )

    actual = doctest.detection_func(lines)
    assert actual == expected


@pytest.mark.parametrize(
    "line",
    (
        pytest.param(textwrap.dedent(lines[8]), id="single line"),
        pytest.param(textwrap.dedent(lines[23]), id="single empty line"),
        pytest.param(textwrap.dedent("\n".join(lines[4:8])), id="multiple lines"),
        pytest.param(
            textwrap.dedent("\n".join(lines[17:23])),
            id="multiple lines with empty continuation line",
        ),
    ),
)
def test_extraction_func(line):
    expected = (
        {"prompt_length": doctest.prompt_length},
        "\n".join(line.lstrip()[4:] for line in line.split("\n")),
    )
    actual = doctest.extraction_func(line)

    assert expected == actual


@pytest.mark.parametrize(
    "expected",
    (
        pytest.param(textwrap.dedent(lines[8]), id="single line"),
        pytest.param(textwrap.dedent(lines[23]), id="single empty line"),
        pytest.param(textwrap.dedent("\n".join(lines[4:8])), id="multiple lines"),
        pytest.param(
            textwrap.dedent("\n".join(lines[17:23])),
            id="multiple lines with empty continuation line",
        ),
    ),
)
def test_reformatting_func(expected):
    line = "\n".join(line.lstrip()[4:] for line in expected.split("\n"))

    actual = doctest.reformatting_func(line)
    assert expected == actual
    assert '"""' not in actual
