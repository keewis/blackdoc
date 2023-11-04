import itertools
import re

import more_itertools

from blackdoc.formats.errors import InvalidFormatError

name = "ipython"

prompt_re = re.compile(r"^(?P<indent>[ ]*)(?P<prompt>In \[(?P<count>\d+)\]: )")
continuation_prompt_re = re.compile(r"^(?P<indent>[ ]*)\.\.\.: ")

prompt_template = "In [{count}]: "
continuation_template = "...: "

magic_re = re.compile(r"^(!.*|%.*|@[a-zA-Z_][a-zA-Z0-9_]* .+)")
magic_comment = "<ipython-magic>"

include_pattern = r"\.pyi?$"


def continuation_lines(lines, indent, prompt_length):
    while True:
        try:
            line_number, line = lines.peek()
        except StopIteration:
            line_number = -1
            line = ""

        match = continuation_prompt_re.match(line)
        if not match or len(match.groupdict()["indent"]) - prompt_length + 5 != indent:
            break

        # actually consume the item
        more_itertools.consume(lines, n=1)

        yield line_number, line


def detection_func(lines):
    try:
        _, line = lines.peek()
    except StopIteration:
        line = ""

    match = prompt_re.match(line)
    if not match:
        return None

    groups = match.groupdict()
    indent = len(groups["indent"])
    prompt_length = len(groups["prompt"])

    detected_lines = list(
        itertools.chain(
            [more_itertools.first(lines)],
            continuation_lines(lines, indent, prompt_length),
        )
    )
    line_numbers, lines = map(tuple, more_itertools.unzip(detected_lines))

    line_range = min(line_numbers), max(line_numbers) + 1
    if line_numbers != tuple(range(line_range[0], line_range[1])):
        raise InvalidFormatError("line numbers are not contiguous")

    return line_range, name, "\n".join(lines)


def is_ipython(line):
    is_prompt = prompt_re.match(line)
    is_continuation_prompt = continuation_prompt_re.match(line)
    return is_prompt or is_continuation_prompt


def metadata(line):
    match = prompt_re.match(line)
    if not match:
        return {}

    groups = match.groupdict()
    return {"count": int(groups["count"])}


def hide_magic(code):
    def comment_magic(line):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if not stripped or not magic_re.match(stripped):
            return line

        return " " * indent + f"# {magic_comment}" + stripped

    lines = code.split("\n")
    processed = tuple(comment_magic(line) for line in lines)

    return "\n".join(processed)


def reveal_magic(code):
    def uncomment_magic(line):
        stripped = line.lstrip()

        if magic_comment not in line:
            return line

        indent = len(line) - len(stripped)
        return " " * indent + stripped[len(magic_comment) + 2 :]

    lines = code.split("\n")
    processed = tuple(uncomment_magic(line) for line in lines)

    return "\n".join(processed)


def extraction_func(code):
    def remove_prompt(line, count):
        n = len(prompt_template.format(count=count))
        return line[n:]

    lines = code.split("\n")
    if len(lines) == 0:
        raise InvalidFormatError("no lines found")

    parameters = metadata(lines[0])

    if not all(is_ipython(line) for line in lines):
        raise InvalidFormatError(f"misformatted code unit: {code}")

    extracted = "\n".join(remove_prompt(line, **parameters) for line in lines)

    return parameters, hide_magic(extracted)


def reformatting_func(line, count):
    prompt = prompt_template.format(count=count)
    continuation_prompt = (
        " " * (len(prompt) - len(continuation_template)) + continuation_template
    )

    lines = iter(reveal_magic(line).split("\n"))

    reformatted = "\n".join(
        itertools.chain(
            more_itertools.always_iterable(prompt + more_itertools.first(lines)),
            (continuation_prompt + line for line in lines),
        )
    )

    return reformatted
