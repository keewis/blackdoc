import argparse
import importlib
import itertools
import sys

from . import print_classification


def format_conflicting_ranges(index_a, index_b, ranges):
    range_a = ranges[index_a]
    range_b = ranges[index_b]
    return f"{range_a} (item {index_a + 1}) ←→ {range_b} (item {index_b + 1})"


def display_data(module):
    lines = module.lines
    labels = module.line_labels
    ranges = module.line_ranges

    labeled = tuple(
        ((start, stop), label, lines[start:stop])
        for (start, stop), label in zip(ranges, labels)
    )
    labeled_line_numbers = tuple(
        tuple(range(start, stop)) for (start, stop), _, _ in labeled
    )
    combinations = itertools.combinations(enumerate(labeled_line_numbers), 2)
    intersections = {
        (index_a, index_b): set(first).intersection(second)
        for (index_a, first), (index_b, second) in combinations
    }
    faulty_ranges = tuple(key for key, value in intersections.items() if value)
    if faulty_ranges:
        formatted_errors = [
            format_conflicting_ranges(index_a, index_b, ranges)
            for index_a, index_b in faulty_ranges
        ]
        print("error: overlapping line ranges:", *formatted_errors, sep="\n -- ")
        return 1

    covered_lines = tuple(itertools.chain.from_iterable(labeled_line_numbers))
    missing_lines = tuple(
        index for index, _ in enumerate(lines) if index not in covered_lines
    )
    missing_ranges = tuple((index, index + 1) for index in missing_lines)
    missing_label = "n/a"
    unlabeled = tuple(
        ((start, stop), missing_label, lines[start:stop])
        for start, stop in missing_ranges
    )
    combined = sorted(
        itertools.chain(labeled, unlabeled),
        key=lambda x: x[0][0],
    )
    print_classification(
        tuple((range_, name, "\n".join(unit)) for range_, name, unit in combined)
    )
    return 0


parser = argparse.ArgumentParser()
parser.add_argument("format", help="print the data of this format")

args = parser.parse_args()
module = importlib.import_module(f".{args.format}", package="blackdoc.tests.data")
sys.exit(display_data(module))
