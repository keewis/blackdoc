from .blacken import blacken
from .classification import detect_format
from .formats import register_format  # noqa


def line_numbers(lines):
    yield from enumerate(lines, start=1)


def format_lines(lines, mode=None):
    numbered = line_numbers(lines)

    labeled = detect_format(numbered)
    blackened = blacken(labeled, mode=mode)

    return blackened
