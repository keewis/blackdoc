import itertools
import re
import textwrap

import more_itertools

from blackdoc.formats.doctest import prompt_re as doctest_prompt_re
from blackdoc.formats.errors import InvalidFormatError
from blackdoc.formats.ipython import hide_magic, reveal_magic
from blackdoc.formats.ipython import prompt_re as ipython_prompt_re

name = "rst"

directive_re = re.compile(
    "(?P<indent>[ ]*).. (?P<name>[a-z][-a-z]*)::(?: (?P<language>[a-z]+))?"
)
option_re = re.compile(r"^\s*:[^:]+:")

include_pattern = r"\.rst$"


def has_prompt(line):
    return any(
        prompt_re.match(line.lstrip())
        for prompt_re in [ipython_prompt_re, doctest_prompt_re]
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
    options = tuple(take_while(lines, lambda x: option_re.match(x[1])))
    newlines = tuple(take_while(lines, lambda x: not x[1].strip()))
    decorator_lines = tuple(take_while(lines, lambda x: x[1].lstrip().startswith("@")))
    _, next_line = lines.peek((0, None))
    if next_line is None:
        return

    if has_prompt(next_line):
        lines.prepend(*options, *newlines, *decorator_lines)
        raise RuntimeError("prompt detected")

    yield from options
    yield from newlines
    yield from decorator_lines

    while True:
        newlines = tuple(take_while(lines, lambda x: not x[1].strip()))
        try:
            line_number, line = lines.peek()
        except StopIteration:
            lines.prepend(*newlines)
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
        line_number, line = lines.peek()
    except StopIteration:
        return None

    match = directive_re.match(line)
    if not match:
        return None

    directive = match.groupdict()

    if directive["name"] not in (
        "code",
        "code-block",
        "ipython",
        "testcode",
        "testsetup",
        "testcleanup",
    ):
        return None

    if directive["language"] not in ("python", None):
        return None

    indent = len(directive.pop("indent"))

    try:
        detected_lines = list(
            itertools.chain(
                [more_itertools.first(lines)],
                continuation_lines(lines, indent),
            )
        )
    except RuntimeError as e:
        if str(e) != "prompt detected":
            raise

        lines.prepend((line_number, line))
        return None

    line_numbers, lines = map(tuple, more_itertools.unzip(detected_lines))
    line_range = min(line_numbers), max(line_numbers) + 1
    if line_numbers != tuple(range(line_range[0], line_range[1])):
        raise RuntimeError("line numbers are not contiguous")

    return line_range, name, "\n".join(lines)


def extraction_func(code):
    lines = more_itertools.peekable(iter(code.split("\n")))

    match = directive_re.fullmatch(more_itertools.first(lines))
    if not match:
        raise InvalidFormatError(f"misformatted code block:\n{code}")

    directive = match.groupdict()
    directive.pop("indent")

    directive["options"] = tuple(
        line.strip() for line in take_while(lines, lambda line: option_re.match(line))
    )

    # correct a missing newline
    newline = lines.peek(None)
    if newline is None:
        raise InvalidFormatError(
            "misformatted code block:"
            " newline after directive options required"
            " but found <end-of-file>"
        )
    elif not newline.strip():
        more_itertools.first(lines)

    lines_ = tuple(lines)
    if len(lines_) == 0:
        raise InvalidFormatError("misformatted code block: could not find any code")

    indent = len(lines_[0]) - len(lines_[0].lstrip())
    directive["prompt_length"] = indent
    directive["n_header_lines"] = len(directive["options"]) + 2

    code_ = hide_magic(textwrap.dedent("\n".join(lines_)))

    return directive, code_


def reformatting_func(code, name, language, options, prompt_length=4):
    indent = " " * prompt_length

    directive = " ".join(
        [f".. {name}::"] + ([language] if language is not None else [])
    )

    options_ = textwrap.indent("\n".join(options), indent) if options else None
    code_ = textwrap.indent(reveal_magic(code), indent)

    return "\n".join(
        line for line in (directive, options_, "", code_) if line is not None
    )
