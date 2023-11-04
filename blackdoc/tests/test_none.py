from blackdoc.formats import none
from blackdoc.tests.data.doctest import lines


def test_detection_func():
    line_range = (1, 2)
    line = lines[0]
    name = none.name

    assert none.detection_func(enumerate(lines, start=1)) == (line_range, name, line)


def test_extraction_func():
    parameters = {}
    line = lines[0]

    assert none.extraction_func(line) == (parameters, line)


def test_reformatting_func():
    line = lines[0]

    assert none.reformatting_func(line) == line
