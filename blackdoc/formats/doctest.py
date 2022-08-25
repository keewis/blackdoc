import itertools
import re

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


def tokenize(code):
    import io
    import tokenize

    readline = io.StringIO(code).readline

    return (
        token
        for token in tokenize.generate_tokens(readline)
        if token.type == tokenize.STRING
    )


def expand_tokens(token):
    length = token.end[0] - token.start[0] + 1
    return [token.string] * length


def detect_docstring_quotes(line):
    def detect_quotes(string):
        if string.startswith("'''"):
            return "'''"
        elif string.startswith('"""'):
            return '"""'
        else:
            return None

    def expand_quotes(quotes, n_lines):
        lines = [None] * n_lines
        for token, quote in quotes.items():
            token_length = token.end[0] - token.start[0] + 1
            lines[token.start[0] - 1 : token.end[0]] = [quote] * token_length
        return lines

    string_tokens = list(tokenize(line))
    quotes = {token: detect_quotes(token.string) for token in string_tokens}
    lines = line.split("\n")
    return expand_quotes(quotes, len(lines))


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


def replace_quotes(line, current, saved):
    if current is None or saved is None:
        return line
    elif current == saved:
        return line
    else:
        return line.replace(current, saved)


def reformatting_func(line, docstring_quotes):
    def add_prompt(prompt, line):
        if not line:
            return prompt

        return " ".join([prompt, line])

    lines = line.rstrip().split("\n")
    if block_start_re.match(lines[0]):
        lines.append("")

    lines = iter(lines)

    reformatted = list(
        itertools.chain(
            more_itertools.always_iterable(
                add_prompt(prompt, more_itertools.first(lines))
            ),
            (add_prompt(continuation_prompt, line) for line in lines),
        )
    )

    # make sure nested docstrings still work
    current_quotes = detect_docstring_quotes("\n".join(reformatted))
    restored = "\n".join(
        replace_quotes(line, current, saved)
        for line, saved, current in itertools.zip_longest(
            reformatted, docstring_quotes, current_quotes
        )
        if line is not None
    )

    return restored
