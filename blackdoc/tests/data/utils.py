def from_dict(labels):
    line_ranges = tuple(
        (
            (lineno - 1, lineno)
            if not isinstance(lineno, tuple)
            else tuple(n - 1 for n in lineno)
        )
        for lineno in labels.keys()
    )
    line_labels = tuple(labels.values())
    return line_ranges, line_labels


def to_classification_format(labels, lines):
    prepared_labels = dict(zip(*from_dict(labels)))
    return tuple(
        ((min_ + 1, max_ + 1), label, "\n".join(lines[min_:max_]))
        for (min_, max_), label in prepared_labels.items()
    )


def format_line_with_range(name, range_, unit):
    min_, max_ = range_
    line_numbers = range(min_, max_)

    no_group = " "
    start_group = "┐"
    mid_group = "│"
    end_group = "┘"

    lines = unit.split("\n")

    def determine_classifier(index):
        if max_ - min_ == 1:
            classifier = no_group
        elif index == 0:
            classifier = start_group
        elif index == max_ - min_ - 1:
            classifier = end_group
        else:
            classifier = mid_group

        return classifier

    return "\n".join(
        f"{name:>8s} {determine_classifier(index)} → {lineno:02d}: {line}"
        for index, (lineno, line) in enumerate(zip(line_numbers, lines))
    )


def format_classification(labeled):
    return "\n".join(
        format_line_with_range(range, name, unit) for name, range, unit in labeled
    )


def print_classification(labeled):
    print(format_classification(labeled))
