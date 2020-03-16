import copy
import re

import black
import more_itertools
from blib2to3.pgen2.tokenize import TokenError

from .formats import detection_funcs, extract_code, reformat_code


def update_line_number(message, original_number):
    line_re = re.compile(r"(?P<line_number>\d+):(?P<column_number>\d+):")
    match = line_re.search(message)
    if match:
        line_number, column_number = map(int, match.groups())
        new_line_number = line_number + original_number - 1

        message = line_re.sub(f"{new_line_number}:{column_number}:", message)
        print(message, tuple(map(int, match.groups())))
    return message


def line_numbers(lines):
    yield from enumerate(lines, start=1)


def classify_lines(lines):
    lines = more_itertools.peekable(lines)
    while lines:
        maybe_detected = (
            (name, func(lines))
            for name, func in detection_funcs.items()
            if name != "none"
        )
        detected = {name: value for name, value in maybe_detected if value is not None}

        if not detected:
            yield detection_funcs["none"](lines)
        elif len(detected) > 1:
            raise RuntimeError(
                f"cannot classify line: {', '.join(detected.values())} claim it: {lines.peek()}"
            )
        else:
            yield more_itertools.one(detected.values())


def blacken(lines, mode=None):
    for original_line_range, category, line_unit in lines:
        if category == "none":
            yield category, line_unit
            continue

        indentation_depth, prompt_length, code = extract_code(line_unit, category)

        current_mode = black.FileMode() if mode is None else copy.copy(mode)
        current_mode.line_length -= indentation_depth + prompt_length

        try:
            blackened = black.format_str(code, mode=current_mode).rstrip()
        except TokenError as e:
            apparent_line_num, column = e.args[1]
            message = e.args[0]
            lineno = original_line_range[0] + (apparent_line_num - 1)
            faulty_line = code.split("\n")[(apparent_line_num - 1) - 1]

            raise black.InvalidInput(f"{lineno}:{column}: {message}: {faulty_line}")
        except black.InvalidInput as e:
            message = update_line_number(str(e), original_line_range[0])
            raise black.InvalidInput(message)

        reformatted = reformat_code(blackened, category, indentation_depth)

        yield category, reformatted


def unclassify(labelled_lines):
    for _, line in labelled_lines:
        yield line


def format_lines(lines, mode=None):
    numbered = line_numbers(lines)

    labeled = classify_lines(numbered)
    blackened = blacken(labeled, mode=mode)

    return unclassify(blackened)
