import ast
import io
import itertools
import re
import sys
import tokenize
from tokenize import TokenError

import more_itertools

from blackdoc.formats.errors import InvalidFormatError

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


def split_by_statement(code_unit):
    """split a code unit into individual statements

    At this point, the only way to have more than a single statement
    is by joining multiple (non-block) statements with a `;`.
    """

    def lineno(node):
        # TODO: remove once we drop support for python=3.7
        version = (sys.version_info.major, sys.version_info.minor)

        if (
            version < (3, 8)
            and isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Str)
        ):
            # bug in ast (fixed in py38): lineno is wrong for multi-line string expressions
            # https://bugs.python.org/issue16806
            n_lines = len(node.value.s.split("\n"))
            lineno = node.lineno - n_lines + 1
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            linenos = [node.lineno] + [dec.lineno for dec in node.decorator_list]
            lineno = min(linenos)
        else:
            lineno = node.lineno

        return lineno

    content = ast.parse(code_unit).body

    lines = code_unit.split("\n")
    if not content:
        return [lines]

    indices = [lineno(obj) - 1 for obj in content]
    # make sure comments are included
    indices[0] = 0
    slices = more_itertools.zip_offset(indices, indices, offsets=(0, 1), longest=True)
    return [lines[start:stop] for start, stop in slices]


def reformatting_func(code_unit, docstring_quotes):
    def is_comment(line):
        return line.lstrip().startswith("#")

    def is_decorator(line):
        return line.lstrip().startswith("@")

    def drop_while(iterable, predicate):
        peekable = more_itertools.peekable(iterable)
        while True:
            try:
                current = peekable.peek()
            except StopIteration:
                break

            if not predicate(current):
                break

            more_itertools.consume(peekable, n=1)

        yield from peekable

    def is_block(lines):
        block_lines = drop_while(
            lines, lambda line: is_comment(line) or is_decorator(line)
        )
        first_line = more_itertools.first(block_lines, default="")
        match = block_start_re.match(first_line)
        return match is not None

    def add_prompt(prompt, line):
        if not line:
            return prompt

        return " ".join([prompt, line])

    def reformat_code_unit(lines):
        if is_block(lines):
            lines.append("")

        lines_ = iter(lines)
        return itertools.chain(
            more_itertools.always_iterable(
                add_prompt(prompt, more_itertools.first(lines_))
            ),
            (add_prompt(continuation_prompt, line) for line in lines_),
        )

    restored_quotes = restore_quotes(code_unit.rstrip(), docstring_quotes)

    subunits = split_by_statement(restored_quotes)

    return "\n".join(
        itertools.chain.from_iterable(reformat_code_unit(unit) for unit in subunits)
    )
