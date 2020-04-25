import itertools
import re

import more_itertools

name = "ipython"

prompt_re = re.compile(r"^(?P<indent>[ ]*)(?P<prompt>In \[(?P<count>\d+)\]: )")
continuation_prompt_re = re.compile(r"^(?P<indent>[ ]*)\.\.\.: ")


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
        raise RuntimeError("line numbers are not contiguous")

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


def extraction_func(line):
    def remove_prompt(line, count):
        n = len(f"In [{count}]: ")
        return line[n:]

    lines = line.split("\n")
    parameters = metadata(lines[0])

    if not all(is_ipython(line) for line in lines):
        raise RuntimeError(f"misformatted code unit: {line}")

    extracted = "\n".join(remove_prompt(line, **parameters) for line in lines)

    return parameters, extracted
