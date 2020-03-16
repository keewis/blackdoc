import more_itertools

from blackdoc import classification

from . import data


def print_line_with_range(name, range_, unit):
    min_, max_ = range_
    line_numbers = range(min_, max_)

    no_group = " "
    start_group = "┐"
    mid_group = "│"
    end_group = "┘"

    for index, (lineno, line) in enumerate(zip(line_numbers, unit.split("\n"))):
        if max_ - min_ == 1:
            classifier = no_group
        elif index == 0:
            classifier = start_group
        elif index == max_ - min_ - 1:
            classifier = end_group
        else:
            classifier = mid_group

        print(f"{name:>8s} {classifier} → {index:02d}: {line}")


def print_classification(labeled):
    for range, name, unit in labeled:
        print_line_with_range(name, range, unit)


def test_classify():
    lines = enumerate(data.lines, start=1)

    classified = tuple(classification.classify(lines))

    print_classification(classified)

    actual = tuple(max_ - min_ for (min_, max_), _, _ in classified)
    expected = data.code_units
    assert expected == actual

    actual = tuple(
        more_itertools.collapse(
            [name] * len(lines.split("\n")) for _, name, lines in classified
        )
    )
    expected = data.line_labels
    assert expected == actual


def test_unclassify():
    labeled = tuple(zip(data.line_labels, data.lines))
    actual = tuple(classification.unclassify(labeled))
    expected = tuple(data.lines)

    assert expected == actual