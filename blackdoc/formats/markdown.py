import itertools
import re
import textwrap

import more_itertools

from blackdoc.formats.errors import InvalidFormatError
from blackdoc.formats.ipython import hide_magic, reveal_magic
from blackdoc.formats.rst import has_prompt

name = "markdown"

# format:
# blocks followed by optional whitespace and the word python
# block fences are three backticks or colons (myst)
# the word can be wrapped by curly braces

directive_re = re.compile(
    r"""(?x)
    ^
    (?P<indent>[ ]*)
    (?P<fences>[`:]{3})
    \s*
    (?:
      (?P<braces>\{\s*(?P<block_type1>[-a-z0-9]+)\s*\})
      |(?P<block_type2>[-a-z0-9]+)
    )
    (?:
      \s+
      (?P<language>[a-z]+)
    )?
    $
    """
)
include_pattern = r"\.md$"
supported_blocks = ("python", "python3", "jupyter-execute", "code-cell")


def preprocess_directive(directive):
    block_type1 = directive.pop("block_type1")
    block_type2 = directive.pop("block_type2")

    new = dict(directive)
    new["block_type"] = block_type1 or block_type2
    new["braces"] = new["braces"] is not None

    return new


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


def extract_options(lines, fences):
    taken = lines.peek()
    line = taken if isinstance(taken, str) else taken[1]

    if line.strip() != "---":
        return ()

    options = [next(lines)]
    # potentially found options
    while True:
        try:
            taken = next(lines)
        except StopIteration:
            break

        options.append(taken)

        line = taken if isinstance(taken, str) else taken[1]
        if line.strip() == "---":
            break
        elif line.strip() == fences:
            lines.prepend(*options)
            return ()

    return tuple(options)


def continuation_lines(lines, indent, fences):
    options = extract_options(lines, fences)
    newlines = tuple(take_while(lines, lambda x: not x[1].strip()))

    _, next_line = lines.peek((0, None))
    if has_prompt(next_line):
        lines.prepend(*options, *newlines)
        raise RuntimeError("prompt detected")

    yield from options
    yield from newlines
    yield from take_while(lines, lambda x: x[1].strip() != fences)


def detection_func(lines):
    try:
        line_number, line = lines.peek()
    except StopIteration:
        return None

    match = directive_re.match(line)
    if not match:
        return None

    directive = preprocess_directive(match.groupdict())
    if directive["block_type"] not in supported_blocks:
        return None
    if directive["block_type"] in {"code-cell"} and directive["language"] != "python":
        return None

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

    directive = preprocess_directive(match.groupdict())
    directive.pop("indent")
    directive["options"] = extract_options(lines, directive["fences"])[1:-1]

    lines_ = tuple(lines)
    if len(lines_) == 0:
        raise InvalidFormatError("misformatted code block: could not find any code")

    indent = len(lines_[0]) - len(lines_[0].lstrip())
    directive["prompt_length"] = indent

    code_ = textwrap.dedent("\n".join(lines_[:-1]))

    return directive, hide_magic(code_)


def reformatting_func(code, block_type, language, fences, braces, options):
    if braces:
        brace_open = "{"
        brace_close = "}"
    else:
        brace_open = ""
        brace_close = ""

    directive = f"{fences}{brace_open}{block_type}{brace_close}"
    if language is not None:
        directive = f"{directive} {language}"
    parts = [directive]
    if options:
        parts.append(
            "\n".join(
                [
                    "---",
                    *options,
                    "---",
                ]
            )
        )
    parts.extend([reveal_magic(code), fences])

    return "\n".join(part for part in parts if part is not None)
