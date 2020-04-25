try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version

from .blacken import blacken
from .classification import detect_format
from .formats import register_format  # noqa

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
