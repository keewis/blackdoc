import functools
import re
import sys

from .blackcompat import wrap_stream_for_windows

colors_re = re.compile("\033" + r"\[[0-9]+(?:;[0-9]+)*m")


def colorize(string, fg=None, bold=False):
    foreground_colors = {
        "white": 37,
        "cyan": 36,
        "green": 32,
        "red": 31,
    }
    bold_code = 1
    reset_code = 0

    codes = []
    if bold:
        codes.append(bold_code)

    if fg:
        codes.append(foreground_colors.get(fg, fg))

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
    lines = contents.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("+++") or line.startswith("---"):
            line = colorize(line, fg="white", bold=True)  # bold white, reset
        elif line.startswith("@@"):
            line = colorize(line, fg="cyan")  # cyan, reset
        elif line.startswith("+"):
            line = colorize(line, fg="green")  # green, reset
        elif line.startswith("-"):
            line = colorize(line, fg="red")  # red, reset
        lines[i] = line
    return "\n".join(lines)
