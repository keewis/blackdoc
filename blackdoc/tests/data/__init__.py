def print_line_with_range(name, range_, unit):
    min_, max_ = range_
    line_numbers = range(min_ + 1, max_ + 1)

    no_group = " "
    start_group = "┐"
    mid_group = "│"
    end_group = "┘"

    lines = unit.split("\n")
    for index, (lineno, line) in enumerate(zip(line_numbers, lines)):
        if max_ - min_ == 1:
            classifier = no_group
        elif index == 0:
            classifier = start_group
        elif index == max_ - min_ - 1:
            classifier = end_group
        else:
            classifier = mid_group

        print(f"{name:>8s} {classifier} → {lineno:02d}: {line}")


def print_classification(labeled):
    for name, range, unit in labeled:
        print_line_with_range(range, name, unit)
