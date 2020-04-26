import itertools
import re
import textwrap

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


def extraction_func(code):
    lines = more_itertools.peekable(iter(code.split("\n")))

    match = directive_re.fullmatch(more_itertools.first(lines))
    if not match:
        raise RuntimeError(f"misformatted code block:\n{code}")

    directive = match.groupdict()
    directive.pop("indent")

    directive["options"] = tuple(
        line.strip() for line in take_while(lines, lambda line: line.strip())
    )

    line = more_itertools.first(lines)
    if line.strip():
        raise RuntimeError(
            f"misformatted code block: newline after options required but found: {line}"
        )

    code = textwrap.dedent("\n".join(lines))

    return directive, code


def reformatting_func(code, name, language, options):
    indent = " " * 4

    directive = " ".join(
        [f".. {name}::"] + ([language] if language is not None else [])
    )

    options_ = textwrap.indent("\n".join(options), indent) if options else None
    code_ = textwrap.indent(code, indent)

    return "\n".join(
        line for line in (directive, options_, "", code_) if line is not None
    )
