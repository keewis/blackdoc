import more_itertools

import blackdoc

raw_docstring = """ a function to open files

    with a very long description

    >>> file = open(
    ...     "very_long_filepath",
    ...     mode="a",
    ... )
    >>> file
    <_io.TextIOWrapper name='very_long_filepath' mode='w' encoding='UTF-8'>

    text after the first example, spanning
    multiple lines

    >>> file.closed
    False
"""
line_labels = (
    "none",
    "none",
    "none",
    "none",
    "doctest",
    "doctest",
    "doctest",
    "doctest",
    "doctest",
    "none",
    "none",
    "none",
    "none",
    "none",
    "doctest",
    "none",
    "none",
)
code_units = (1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1)
docstring = """ a function to open files

    with a very long description

    >>> file = open("very_long_filepath", mode="a",)
    >>> file
    <_io.TextIOWrapper name='very_long_filepath' mode='w' encoding='UTF-8'>

    text after the first example, spanning
    multiple lines

    >>> file.closed
    False
"""

prompts = (
    None,
    None,
    None,
    None,
    ">>> ",
    "... ",
    "... ",
    "... ",
    ">>> ",
    None,
    None,
    None,
    None,
    None,
    ">>> ",
    None,
    None,
)


def test_extract_prompt():
    extracted = tuple(
        blackdoc.extract_prompt(line) for line in raw_docstring.split("\n")
    )
    assert extracted == prompts


def test_classify():
    categories, _ = more_itertools.unzip(blackdoc.classify(raw_docstring.split("\n")))

    assert tuple(categories) == line_labels


def test_unclassify():
    labelled_lines = zip(line_labels, raw_docstring.split("\n"))
    lines = blackdoc.unclassify(labelled_lines)

    assert "\n".join(lines) == raw_docstring


def test_group_code_units():
    labelled_lines = list(zip(line_labels, raw_docstring.split("\n")))
    grouped = list(blackdoc.group_code_units(labelled_lines))

    assert tuple(len(unit.split("\n")) for _, unit in grouped) == code_units


def test_blacken():
    def join(group):
        if len(group) == 1:
            return group

        categories, lines = more_itertools.unzip(group)
        return more_itertools.first(categories), "\n".join(lines)

    labelled_lines = zip(line_labels, raw_docstring.split("\n"))
    grouped = (
        tuple(more_itertools.collapse(join(group)))
        for group in more_itertools.split_into(labelled_lines, code_units)
    )

    formatted = blackdoc.blacken(grouped)
    formatted_docstring = "\n".join(unit for _, unit in formatted)

    assert formatted_docstring == docstring
