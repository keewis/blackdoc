import copy
import pathlib
import sys
import textwrap

import black
import more_itertools

doctest_prompt = ">>> "
doctest_continuation_prompt = "... "

prompt_categories = {
    "doctest": doctest_prompt,
}
continuation_prompt_categories = {
    "doctest": doctest_continuation_prompt,
}
available_prompts = set(prompt_categories.values()) | set(
    continuation_prompt_categories.values()
)


def extract_prompt(line):
    stripped = line.lstrip()
    prompt_length = stripped.find(" ") + 1

    prompt = stripped[:prompt_length]

    return prompt if prompt in available_prompts else None


def remove_prompt(line, prompt):
    if not line.startswith(prompt):
        raise RuntimeError(
            f"cannot remove prompt {prompt} from line: prompt not found", line
        )

    without_prompt = line[len(prompt) :]
    return without_prompt


def add_prompt(line, prompt):
    return prompt + line


def remove_doctest_prompt(code_unit):
    indentation_depth = code_unit.find(doctest_prompt)
    code_unit = textwrap.dedent(code_unit)

    # multiline unit
    if "\n" in code_unit:
        prompt_line, *continuation_lines = code_unit.split("\n")
        removed = "\n".join(
            [
                remove_prompt(prompt_line, doctest_prompt),
                *(
                    remove_prompt(line, doctest_continuation_prompt)
                    for line in continuation_lines
                ),
            ]
        )
    else:
        removed = remove_prompt(code_unit, doctest_prompt)

    return indentation_depth, removed


def add_doctest_prompt(code_unit, indentation_depth):
    if "\n" in code_unit:
        prompt_line, *continuation_lines = code_unit.split("\n")
        reformatted = "\n".join(
            [
                add_prompt(prompt_line, doctest_prompt),
                *(
                    add_prompt(line, doctest_continuation_prompt)
                    for line in continuation_lines
                ),
            ]
        )
    else:
        reformatted = add_prompt(code_unit, doctest_prompt)

    return textwrap.indent(reformatted, " " * indentation_depth)


extraction_funcs = {
    "doctest": remove_doctest_prompt,
}
reformatting_funcs = {
    "doctest": add_doctest_prompt,
}


def classify(lines):
    """ classify lines by prompt type """
    prompts = dict(zip(prompt_categories.values(), prompt_categories.keys()))
    continuation_prompts = dict(
        zip(
            continuation_prompt_categories.values(),
            continuation_prompt_categories.keys(),
        )
    )

    for line in lines:
        maybe_prompt = extract_prompt(line)
        category = (
            prompts.get(maybe_prompt, None)
            or continuation_prompts.get(maybe_prompt, None)
            or "none"
        )

        yield category, line


def continuation_lines(lines, continuation_prompt):
    # We can't use `itertools.takewhile` because it drops the first non-match
    # Instead, we peek at the iterable and only remove the element if we take it
    iterable = more_itertools.peekable(lines) if not hasattr(lines, "peek") else lines
    while True:
        try:
            category, line = iterable.peek()
        except StopIteration:
            break

        if extract_prompt(line) != continuation_prompt:
            break

        # consume the item
        next(iterable)

        yield line


def group_code_units(labelled_lines):
    """ group together code units """
    # we need to make this peekable here since otherwise we lose an element
    lines = more_itertools.peekable(labelled_lines)
    while True:
        try:
            category, line = next(lines)
        except StopIteration:
            break

        if category == "none":
            unit = line
        else:
            continuation_prompt = continuation_prompt_categories.get(category, None)
            if continuation_prompt is None:
                raise ValueError("unknown prompt category for grouping: {category}")
            unit = "\n".join([line, *continuation_lines(lines, continuation_prompt)])
        yield category, unit


def blacken(labelled_lines, mode=None):
    for category, line in labelled_lines:
        if category == "none":
            yield category, line
            continue

        # remove the prompt and save the indentation depth for later
        converter = extraction_funcs.get(category, None)
        if converter is None:
            raise ValueError(f"unknown prompt category for extraction: {category}")
        indentation_depth, code_unit = converter(line)

        # update the line length
        prompt_length = indentation_depth + len(prompt_categories[category])
        current_mode = black.FileMode() if mode is None else copy.copy(mode)
        current_mode.line_length -= prompt_length

        # blacken the code
        blackened = black.format_str(code_unit, mode=current_mode).rstrip()

        # add the prompt and reindent
        converter = reformatting_funcs.get(category, None)
        if converter is None:
            raise ValueError(f"unknown prompt category for reformatting: {category}")

        reformatted = converter(blackened, indentation_depth)
        yield category, reformatted


def unclassify(labelled_lines):
    for _, line in labelled_lines:
        yield line


def format_lines(lines):
    labeled = classify(lines)
    grouped = group_code_units(labeled)
    blackened = blacken(grouped)

    return unclassify(blackened)


def format_file(path):
    with open(path) as f:
        return "\n".join(format_lines(line.rstrip() for line in f)) + "\n"


def format_text(text):
    return "\n".join(format_lines(text.split("\n")))


def collect_files(path):
    pass


def process(args):
    if not args.src:
        print("No Path provided. Nothing to do 😴")
        return 0

    mode = black.FileMode(line_length=args.line_length)
    mode


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="run black on documentation code snippets (e.g. doctest)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-t",
        "--target-versions",
        action="append",
        choices=[v.name.lower() for v in black.TargetVersion],
        help=(
            "Python versions that should be supported by Black's output. (default: "
            "per-file auto-detection)"
        ),
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-l",
        "--line-length",
        metavar="INT",
        type=int,
        default=black.DEFAULT_LINE_LENGTH,
        help="How many characters per line to allow.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Don't write the files back, just return the status.  Return code 0 "
            "means nothing would change.  Return code 1 means some files would be "
            "reformatted.  Return code 123 means there was an internal error."
        ),
    )
    parser.add_argument(
        "--include",
        metavar="TEXT",
        type=str,
        default=black.DEFAULT_INCLUDES,
        help=(
            "A regular expression that matches files and directories that should be "
            "included on recursive searches.  An empty value means all files are "
            "included regardless of the name.  Use forward slashes for directories on "
            "all platforms (Windows, too).  Exclusions are calculated first, inclusions "
            "later."
        ),
    )
    parser.add_argument(
        "--exclude",
        metavar="TEXT",
        type=str,
        default=black.DEFAULT_EXCLUDES,
        help=(
            "A regular expression that matches files and directories that should be "
            "excluded on recursive searches.  An empty value means no paths are excluded. "
            "Use forward slashes for directories on all platforms (Windows, too).  "
            "Exclusions are calculated first, inclusions later."
        ),
    )
    parser.add_argument(
        "src",
        action="store",
        type=pathlib.Path,
        nargs="*",
        default=None,
        help="one or more paths to work on",
    )

    args = parser.parse_args()
    sys.exit(process(args))
