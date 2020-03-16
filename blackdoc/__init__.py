from .blacken import blacken
from .classification import classify, unclassify


def line_numbers(lines):
    yield from enumerate(lines, start=1)


def format_lines(lines, mode=None):
    numbered = line_numbers(lines)

    labeled = classify(numbered)
    blackened = blacken(labeled, mode=mode)

    return unclassify(blackened)
