from blackdoc.formats import none

from .data import docstring


def test_detection_func():
    lines = docstring.split("\n")

    line_range = (1, 2)
    line = lines[0]

    assert none.detection_func(enumerate(lines, start=1)) == (line_range, line)


def test_extraction_func():
    lines = docstring.split("\n")
    depth = 0
    line = lines[0]

    assert none.extraction_func(line) == (depth, line)


def test_reformatting_func():
    lines = docstring.split("\n")
    line = lines[0]

    assert none.reformatting_func(line, indentation_depth=0) == line
