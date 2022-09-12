import io
import itertools
import re
import tokenize
from tokenize import TokenError

import more_itertools

from .errors import InvalidFormatError

name = "doctest"
prompt_length = 4
prompt = ">>>"
prompt_re = re.compile(r"(>>> ?)")
continuation_prompt = "..."
continuation_prompt_re = re.compile(r"(\.\.\. ?)")
include_pattern = r"\.pyi?$"
block_start_re = re.compile(r"^[^#:]+:(\s*#.*)?$")


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
        raise InvalidFormatError("line numbers are not contiguous")

    return line_range, name, "\n".join(lines)


def suppress(iterable, errors):
    iter_ = iter(iterable)
    while True:
        try:
            yield next(iter_)
        except errors:
            yield None
        except StopIteration:
            break


def tokenize_string(code):
    readline = io.StringIO(code).readline

    return tokenize.generate_tokens(readline)


def extract_string_tokens(code):
    tokens = tokenize_string(code)

    # suppress invalid code errors: `black` will raise with a better error message
    return (
        token
        for token in suppress(tokens, TokenError)
        if token is not None and token.type == tokenize.STRING
    )


def detect_docstring_quotes(code_unit):
    def extract_quotes(string):
        if string.startswith("'''") and string.endswith("'''"):
            return "'''"
        elif string.startswith('"""') and string.endswith('"""'):
            return '"""'
        else:
            return None

    string_tokens = list(extract_string_tokens(code_unit))
    token_quotes = {token: extract_quotes(token.string) for token in string_tokens}
    quotes = (quote for quote in token_quotes.values() if quote is not None)

    return more_itertools.first(quotes, None)


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
        raise InvalidFormatError(f"misformatted code unit: {line}")

    extracted_line = "\n".join(remove_prompt(line) for line in lines)
    docstring_quotes = detect_docstring_quotes(extracted_line)

    return {
        "prompt_length": len(prompt) + 1,
        "docstring_quotes": docstring_quotes,
    }, extracted_line


def restore_quotes(code_unit, original_quotes):
    def line_offsets(code_unit):
        offsets = [m.end() for m in re.finditer("\n", code_unit)]

        return {lineno: offset for lineno, offset in enumerate([0] + offsets, start=1)}

    def compute_offset(pos, offsets):
        lineno, charno = pos
        return offsets[lineno] + charno

    if original_quotes is None:
        return code_unit

    to_replace = "'''" if original_quotes == '"""' else '"""'

    string_tokens = extract_string_tokens(code_unit)
    triple_quote_tokens = [
        token
        for token in string_tokens
        if token.string.startswith(to_replace) and token.string.endswith(to_replace)
    ]

    offsets = line_offsets(code_unit)
    mutable_string = io.StringIO(code_unit)
    for token in triple_quote_tokens:
        # find the offset in the stream
        start = compute_offset(token.start, offsets)
        end = compute_offset(token.end, offsets) - 3

        mutable_string.seek(start)
        mutable_string.write(original_quotes)

        mutable_string.seek(end)
        mutable_string.write(original_quotes)

    restored_code_unit = mutable_string.getvalue()

    return restored_code_unit


def reformatting_func(code_unit, docstring_quotes):
    def add_prompt(prompt, line):
        if not line:
            return prompt

        return " ".join([prompt, line])

    restored_quotes = restore_quotes(code_unit, docstring_quotes)

    lines = restored_quotes.rstrip().split("\n")
    if block_start_re.match(lines[0]):
        lines.append("")

    lines_ = iter(lines)
    reformatted = list(
        itertools.chain(
            more_itertools.always_iterable(
                add_prompt(prompt, more_itertools.first(lines_))
            ),
            (add_prompt(continuation_prompt, line) for line in lines_),
        )
    )

    return "\n".join(reformatted)
