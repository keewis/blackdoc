import functools
import re
import sys

from .blackcompat import wrap_stream_for_windows

# TODO: use rich instead

colors_re = re.compile("\033" + r"\[[0-9]+(?:;[0-9]+)*m")
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
