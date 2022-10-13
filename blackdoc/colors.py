import functools
import itertools
import re
import sys

from rich.highlighter import Highlighter

from .blackcompat import wrap_stream_for_windows

# TODO: use rich instead

colors_re = re.compile("\033" + r"\[[0-9]+(?:;[0-9]+)*m")
line_re = re.compile("\n")
trailing_whitespace_re = re.compile(r"\s+$")


def colorize(string, fg=None, bg=None, bold=False):
    foreground_colors = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "purple": 35,
        "cyan": 36,
        "white": 37,
    }
    background_colors = {
        "black": 40,
        "red": 41,
        "green": 42,
        "yellow": 43,
        "blue": 44,
        "purple": 45,
        "cyan": 46,
        "white": 47,
    }
    bold_code = 1
    reset_code = 0

    codes = []
    if bold:
        codes.append(bold_code)

    if fg:
        codes.append(foreground_colors.get(fg, fg))
    if bg:
        codes.append(background_colors.get(bg, bg))

    return f"\033[{';'.join(map(str, codes))}m{string}\033[{reset_code}m"


def remove_colors(message):
    return "".join(colors_re.split(message))


# signature inspired by click.secho
def custom_print(message, end="\n", file=sys.stdout, **styles):
    if file.isatty():
        message = colorize(message, **styles)
    else:
        message = remove_colors(message)

    print(message, end=end, file=wrap_stream_for_windows(file))


out = functools.partial(custom_print, file=sys.stdout)
err = functools.partial(custom_print, file=sys.stderr)


def color_diff(contents):
    """Inject the ANSI color codes to the diff."""

    def colorize_line(line):
        if line.startswith("+++") or line.startswith("---"):
            line = colorize(line, fg="white", bold=True)
        elif line.startswith("@@"):
            line = colorize(line, fg="cyan")
        elif line.startswith("+"):
            line = colorize(line, fg="green")
        elif line.startswith("-"):
            match = trailing_whitespace_re.search(line)
            line = colorize(line.rstrip(), fg="red")
            if match:
                whitespace = match.group(0)
                line += colorize(whitespace, bg="red")

        return line

    lines = contents.split("\n")
    return "\n".join(colorize_line(line) for line in lines)


def line_style(lineno, line):
    if line.startswith("+++") or line.startswith("---"):
        yield lineno, (0, len(line)), "bold white"
    elif line.startswith("@@"):
        yield lineno, (0, len(line)), "cyan"
    elif line.startswith("+"):
        yield lineno, (0, len(line)), "green"
    elif line.startswith("-"):
        yield lineno, (0, len(line)), "red"
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
