import itertools
import re

from rich.highlighter import Highlighter

line_re = re.compile("\n")
trailing_whitespace_re = re.compile(r"\s+$")


def line_style(lineno, line):
    if line.startswith("+++") or line.startswith("---"):
        yield lineno, (0, len(line)), "bold"
    elif line.startswith("@@"):
        yield lineno, (0, len(line)), "cyan"
    elif line.startswith("+"):
        yield lineno, (0, len(line)), "green"
    elif line.startswith("-"):
        yield lineno, (0, len(line.rstrip())), "red"
        trailing_whitespace = trailing_whitespace_re.search(line)
        if trailing_whitespace:
            start, end = trailing_whitespace.span()
            yield lineno, (start, end), "red on red"
    else:
        yield lineno, (0, len(line)), ""


def line_offsets(text):
    matches = line_re.finditer(text)

    return [0] + [m.end() for m in matches]


def move_span(start, end, offset):
    return start + offset, end + offset


class DiffHighlighter(Highlighter):
    def highlight(self, text):
        def diff_styles(text):
            lines = text.split("\n")
            line_styles = itertools.chain.from_iterable(
                line_style(lineno, line) for lineno, line in enumerate(lines, start=1)
            )

            offsets = line_offsets(text)
            styles = {
                move_span(start, end, offsets[lineno - 1]): style
                for lineno, (start, end), style in line_styles
            }

            yield from styles.items()

        for (start, end), style in diff_styles(text.plain):
            text.stylize(style, start=start, end=end)


class FileHighlighter(Highlighter):
    highlights = {
        r"[0-9]+ files?(?!.*fail)": "blue",
        r"^.+reformatted$": "bold",
        r"^.+fail.+$": "red",
    }

    def highlight(self, text):
        for highlight_re, style in self.highlights.items():
            text.highlight_regex(highlight_re, style=style)
