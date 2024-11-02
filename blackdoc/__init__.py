from importlib.metadata import version

from blackdoc.blacken import blacken
from blackdoc.classification import detect_format
from blackdoc.formats import InvalidFormatError, register_format  # noqa: F401

try:
    __version__ = version("blackdoc")
except Exception:
    # Local copy or not installed with setuptools.
    # Disable minimum version checks on downstream libraries.
    __version__ = "999"


def line_numbers(lines):
    yield from enumerate(lines, start=1)


def format_lines(lines, mode=None):
    numbered = line_numbers(lines)

    labeled = detect_format(numbered)
    blackened = blacken(labeled, mode=mode)

    return blackened
