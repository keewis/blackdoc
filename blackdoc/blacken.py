import copy
import re
import textwrap

import black
from blib2to3.pgen2.tokenize import TokenError

from blackdoc.formats import extract_code, reformat_code


def parse_message(message):
    line_re = re.compile(
        r"^(?P<message>[^:]+): (?P<line_number>\d+):"
        r"(?P<column_number>\d+)(?:(?::[\w]+)(?P<faulty_line>.+))?"
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

    values = match.groupdict()
    if values["faulty_line"] is None:
        # try multiline format
        lines = message.splitlines()
        # skip standard message
        values["faulty_line"] = textwrap.indent("\n".join(lines[1:]), "  ")

    return tuple(types[key](value) for key, value in values.items())


def blacken(lines, mode=None):
    for original_line_range, code_format, line_unit in lines:
        if code_format == "none":
            yield line_unit
            continue

        indentation_depth, parameters, code = extract_code(line_unit, code_format)

        current_mode = black.FileMode() if mode is None else copy.copy(mode)
        current_mode.line_length -= indentation_depth + parameters.pop(
            "prompt_length", 0
        )

        original_line_number, _ = original_line_range
        original_line_number += parameters.pop("n_header_lines", 0)

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

            common = f"{message}: {lineno}:{column}:"
            sep = "\n" if len(faulty_line.splitlines()) > 1 else " "
            raise black.InvalidInput(sep.join([common, faulty_line]))
        except IndentationError as e:
            lineno = original_line_number + (e.lineno - 1)
            line = e.text.rstrip()

            # TODO: try to find the actual line, this exception is
            # only raised when the indentation causes the code to
            # become ambiguous
            raise black.InvalidInput(f"Invalid indentation: {lineno}: {line}")

        reformatted = reformat_code(
            blackened, code_format, indentation_depth, **parameters
        )

        yield reformatted
