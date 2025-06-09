import itertools
import re
import textwrap

import more_itertools

from blackdoc.formats.errors import InvalidFormatError

name = "markdown"

# format:
# blocks followed by optional whitespace and the word python
# block fences are three backticks or colons (myst)
# the word can be wrapped by curly braces

directive_re = re.compile(
    r"(?P<indent>[ ]*)(?P<fences>[`:]{3})\s*\{?\s*(?P<language>python)\s*\}?"
)
include_pattern = r"\.md$"


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


def continuation_lines(lines, indent, fences):
    yield from take_while(lines, lambda x: x[1].strip() != fences)


def detection_func(lines):
    try:
        line_number, line = lines.peek()
    except StopIteration:
        return None

    match = directive_re.match(line)
    if not match:
        return None

    directive = match.groupdict()
    indent = len(directive.pop("indent"))

    start_line = more_itertools.first(lines)
    try:
        content_lines = list(continuation_lines(lines, indent, directive["fences"]))
    except RuntimeError as e:
        if str(e) != "prompt detected":
            raise

        lines.prepend((line_number, line))
        return None

    try:
        line_number, stop_line = lines.peek()
    except StopIteration:
        line_number = -1
        stop_line = None

    if stop_line.strip() != directive.get("fences"):
        raise RuntimeError("found a code block without closing fence")

    detected_lines = list(
        itertools.chain([start_line], content_lines, [more_itertools.first(lines)])
    )

    line_numbers, lines = map(tuple, more_itertools.unzip(detected_lines))
    line_range = min(line_numbers), max(line_numbers) + 2
    if line_numbers != tuple(range(line_range[0], line_range[1] - 1)):
        raise RuntimeError("line numbers are not contiguous")

    return line_range, name, "\n".join(lines)


def extraction_func(code):
    lines = more_itertools.peekable(iter(code.split("\n")))

    match = directive_re.fullmatch(more_itertools.first(lines))
    if not match:
        raise InvalidFormatError(f"misformatted code block:\n{code}")

    directive = match.groupdict()
    directive.pop("indent")

    lines_ = tuple(lines)
    if len(lines_) == 0:
        raise InvalidFormatError("misformatted code block: could not find any code")

    indent = len(lines_[0]) - len(lines_[0].lstrip())
    directive["prompt_length"] = indent

    code_ = textwrap.dedent("\n".join(lines_[:-1]))

    return directive, code_


def reformatting_func(code, language, fences):
    directive = f"{fences}{language}"

    return "\n".join(line for line in (directive, code, fences) if line is not None)
