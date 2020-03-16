from blackdoc.formats import none

from .data import docstring


def test_detection_func():
    lines = docstring.split("\n")

    line_range = (1, 2)
    line = lines[0]

    assert none.detection_func(enumerate(lines, start=1)) == (line_range, line)


def test_extraction_func():
    lines = docstring.split("\n")
    line = lines[0]

    assert none.extraction_func(line) == line


def test_reformatting_func():
    lines = docstring.split("\n")
    line = lines[0]

    assert none.reformatting_func(line) == line
