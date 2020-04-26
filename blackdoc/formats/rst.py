import itertools
import re

import more_itertools

name = "rst"

directive_re = re.compile(
    "(?P<indent>[ ]*).. (?P<name>[a-z][-a-z]*)::(?: (?P<language>[a-z]+))?"
)


def take_while(iterable, predicate):
    while True:
        try:
            taken = next(iterable)
        except StopIteration:
            break

        if not predicate(taken):
            iterable.prepend(taken)
            break

        yield taken


def continuation_lines(lines, indent):
    while True:
        newlines = tuple(take_while(lines, lambda x: not x[1].strip()))
        try:
            line_number, line = lines.peek()
        except StopIteration:
            break

        current_indent = len(line) - len(line.lstrip())
        if current_indent <= indent:
            # put back the newlines, if any
            lines.prepend(*newlines)
            break

        yield from newlines

        # consume the line
        more_itertools.consume(lines, n=1)

        yield line_number, line


def detection_func(lines):
    try:
        _, line = lines.peek()
    except StopIteration:
        line = ""

    match = directive_re.match(line)
    if not match:
        return None

    directive = match.groupdict()

    if directive["name"] not in ("code", "code-block", "ipython"):
        return None

    indent = len(directive.pop("indent"))
    detected_lines = list(
        itertools.chain(
            [more_itertools.first(lines)], continuation_lines(lines, indent),
        )
    )

    line_numbers, lines = map(tuple, more_itertools.unzip(detected_lines))
    line_range = min(line_numbers), max(line_numbers) + 1
    if line_numbers != tuple(range(line_range[0], line_range[1])):
        raise RuntimeError("line numbers are not contiguous")

    return line_range, name, "\n".join(lines)
