import textwrap

import more_itertools
import pytest

from blackdoc.formats import ipython

from .data import ipython as data


@pytest.mark.parametrize(
    "lines,expected",
    (
        pytest.param(data.lines[0], None, id="no_line"),
        pytest.param(
            data.lines[8], ((1, 2), ipython.name, data.lines[8]), id="single_line"
        ),
        pytest.param(
            data.lines[4:8],
            ((1, 5), ipython.name, "\n".join(data.lines[4:8])),
            id="multiple_lines",
        ),
    ),
)
def test_detection_func(lines, expected):
    lines = more_itertools.peekable(
        enumerate(more_itertools.always_iterable(lines), start=1)
    )

    actual = ipython.detection_func(lines)
    assert actual == expected


@pytest.mark.parametrize(
    "line,expected",
    (
        pytest.param(
            textwrap.dedent(data.lines[8]),
            ({"count": 2}, textwrap.dedent(data.lines[8])[8:]),
            id="single_line",
        ),
        pytest.param(
            textwrap.dedent("\n".join(data.lines[4:8])),
            ({"count": 1}, "\n".join(line[12:] for line in data.lines[4:8])),
            id="multiple_lines",
        ),
    ),
)
def test_extraction_func(line, expected):
    actual = ipython.extraction_func(line)

    assert expected == actual


@pytest.mark.parametrize(
    "expected",
    (
        pytest.param(textwrap.dedent(data.lines[8]), id="single_line"),
        pytest.param(textwrap.dedent("\n".join(data.lines[4:8])), id="multiple_lines"),
    ),
)
def test_reformatting_func(expected):
    line = "\n".join(line.lstrip()[4:] for line in expected.split("\n"))

    actual = ipython.reformatting_func(line)
    assert expected == actual
