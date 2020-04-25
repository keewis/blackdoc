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
        pytest.param(textwrap.dedent(lines[8]), id="single_line"),
        pytest.param(textwrap.dedent("\n".join(lines[4:8])), id="multiple_lines"),
    ),
)
def test_extraction_func(line):
    prompt_length = len(doctest.prompt)
    expected = (
        {"prompt_length": prompt_length},
        "\n".join(line.lstrip()[4:] for line in line.split("\n")),
    )
    actual = doctest.extraction_func(line)

    assert expected == actual


@pytest.mark.parametrize(
    "expected",
    (
        pytest.param(textwrap.dedent(lines[8]), id="single_line"),
        pytest.param(textwrap.dedent("\n".join(lines[4:8])), id="multiple_lines"),
    ),
)
def test_reformatting_func(expected):
    line = "\n".join(line.lstrip()[4:] for line in expected.split("\n"))

    actual = doctest.reformatting_func(line)
    assert expected == actual
