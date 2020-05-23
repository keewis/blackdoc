import itertools

import more_itertools

name = "doctest"
prompt = ">>> "
continuation_prompt = "... "
include_pattern = r"\.pyi?$"


def continuation_lines(lines):
    while True:
        try:
            line_number, line = lines.peek()
        except StopIteration:
            line_number = -1
            line = ""

        if not line.lstrip().startswith(continuation_prompt):
            break

        # actually consume the item
        more_itertools.consume(lines, n=1)

        yield line_number, line


def detection_func(lines):
    try:
        _, line = lines.peek()
    except StopIteration:
        line = ""

    if not line.lstrip().startswith(prompt):
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
    lines = line.split("\n")
    if any(line[:4] not in (prompt, continuation_prompt) for line in lines):
        raise RuntimeError(f"misformatted code unit: {line}")

    extracted_line = "\n".join(line[4:] for line in lines)

    return {"prompt_length": len(prompt)}, extracted_line


def reformatting_func(line):
    lines = iter(line.split("\n"))

    reformatted = "\n".join(
        itertools.chain(
            more_itertools.always_iterable(prompt + more_itertools.first(lines)),
            (continuation_prompt + line for line in lines),
        )
    )
    return reformatted
