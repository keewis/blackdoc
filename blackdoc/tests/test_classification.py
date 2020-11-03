import more_itertools

from blackdoc import classification

from .data import doctest as data
from .data import print_classification


def test_detect_format():
    lines = enumerate(data.lines, start=1)

    labeled = tuple(classification.detect_format(lines))

    print_classification(labeled)

    actual = tuple(max_ - min_ for (min_, max_), _, _ in labeled)
    expected = data.code_units
    assert expected == actual

    actual = tuple(
        more_itertools.collapse(
            [name] * len(lines.split("\n")) for _, name, lines in labeled
        )
    )
    expected = data.line_labels
    assert expected == actual
