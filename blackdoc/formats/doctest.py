import itertools
import re

import more_itertools

name = "doctest"
prompt_length = 4
prompt = ">>>"
prompt_re = re.compile(r"(>>> ?)")
continuation_prompt = "..."
continuation_prompt_re = re.compile(r"(\.\.\. ?)")
include_pattern = r"\.pyi?$"


def continuation_lines(lines):
    while True:
        try:
            line_number, line = lines.peek()
        except StopIteration:
            line_number = -1
            line = ""

        if not continuation_prompt_re.match(line.lstrip()):
            break

        # actually consume the item
        more_itertools.consume(lines, n=1)

        yield line_number, line


def detection_func(lines):
    try:
        _, line = lines.peek()
    except StopIteration:
        line = ""

    if not prompt_re.match(line.lstrip()):
        return None

    detected_lines = list(
        itertools.chain([more_itertools.first(lines)], continuation_lines(lines))
    )
    line_numbers, lines = map(tuple, more_itertools.unzip(detected_lines))

    line_range = min(line_numbers), max(line_numbers) + 1
    if line_numbers != tuple(range(line_range[0], line_range[1])):
        raise RuntimeError("line numbers are not contiguous")

    return line_range, name, "\n".join(lines)


def extraction_func(line):
    def extract_prompt(line):
        match = prompt_re.match(line)
        if match is not None:
            (prompt,) = match.groups()
            return prompt

        match = continuation_prompt_re.match(line)
        if match is not None:
            (prompt,) = match.groups()
            return prompt

        return ""

    def remove_prompt(line):
        prompt = extract_prompt(line)
        return line[len(prompt) :]

    lines = line.split("\n")
    if any(
        extract_prompt(line).rstrip() not in (prompt, continuation_prompt)
        for line in lines
    ):
        raise RuntimeError(f"misformatted code unit: {line}")

    extracted_line = "\n".join(remove_prompt(line) for line in lines)

    return {"prompt_length": len(prompt) + 1}, extracted_line


def reformatting_func(line):
    def add_prompt(prompt, line):
        if not line:
            return prompt

        return " ".join([prompt, line])

    lines = iter(line.split("\n"))

    reformatted = "\n".join(
        itertools.chain(
            more_itertools.always_iterable(
                add_prompt(prompt, more_itertools.first(lines))
            ),
            (add_prompt(continuation_prompt, line) for line in lines),
        )
    )
    return reformatted
