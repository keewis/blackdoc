from blackdoc import classification

from .data import doctest as data
from .data import print_classification


def test_detect_format():
    lines = enumerate(data.lines)

    labeled = tuple(classification.detect_format(lines))

    print_classification(labeled)

    actual = tuple(range_ for range_, _, _ in labeled)
    expected = data.line_ranges
    assert expected == actual

    actual = tuple(name for _, name, _ in labeled)
    expected = data.line_labels
    assert expected == actual
