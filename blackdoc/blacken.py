import copy
import re

import black
from blib2to3.pgen2.tokenize import TokenError

from .formats import extract_code, reformat_code


def parse_message(message):
    line_re = re.compile(
        r"^(?P<message>[^:]+): (?P<line_number>\d+):"
        r"(?P<column_number>\d+): (?P<faulty_line>.+)$"
    )

    types = {
        "message": str,
        "line_number": int,
        "column_number": int,
        "faulty_line": str,
    }

    match = line_re.match(message)
    if match is None:
        raise ValueError(f"invalid error message: {message}")

    return tuple(types[key](value) for key, value in match.groupdict().items())


def blacken(lines, mode=None):
    for original_line_range, category, line_unit in lines:
        if category == "none":
            yield line_unit
            continue

        indentation_depth, prompt_length, code = extract_code(line_unit, category)

        current_mode = black.FileMode() if mode is None else copy.copy(mode)
        current_mode.line_length -= indentation_depth + prompt_length

        original_line_number, _ = original_line_range

        try:
            blackened = black.format_str(code, mode=current_mode).rstrip()
        except TokenError as e:
            message, (apparent_line_number, column) = e.args

            lineno = original_line_number + (apparent_line_number - 1)
            faulty_line = code.split("\n")[(apparent_line_number - 1) - 1]

            raise black.InvalidInput(
                f"Cannot parse: {lineno}:{column}: {message}: {faulty_line}"
            )
        except black.InvalidInput as e:
            message, apparent_line_number, column, faulty_line = parse_message(str(e))

            lineno = original_line_number + (apparent_line_number - 1)
            raise black.InvalidInput(f"{message}: {lineno}:{column}: {faulty_line}")

        reformatted = reformat_code(blackened, category, indentation_depth)

        yield reformatted
