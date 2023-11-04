from blackdoc.tests.data.utils import from_dict

docstring = """ a function to open files

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

    >>> ''' arbitrary triple-quoted string
    ...
    ... with a empty continuation line
    ... '''
    >>> def myfunc2(arg1, arg2):
    ...     pass
    >>>

    >>> if myfunc2(2, 1) is not None:
    ...     print("caught")
    >>> a = 2
    ...
    >>> # this is not a block:
"""
lines = docstring.split("\n")
labels = {
    1: "none",
    2: "none",
    3: "none",
    4: "none",
    (5, 9): "doctest",
    9: "doctest",
    10: "none",
    11: "none",
    12: "none",
    13: "none",
    14: "none",
    15: "doctest",
    16: "none",
    17: "none",
    (18, 22): "doctest",
    (22, 24): "doctest",
    24: "doctest",
    25: "none",
    (26, 28): "doctest",
    (28, 30): "doctest",
    30: "doctest",
    31: "none",
}
line_ranges, line_labels = from_dict(labels)

expected = """ a function to open files

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

    >>> ''' arbitrary triple-quoted string
    ...
    ... with a empty continuation line
    ... '''
    >>> def myfunc2(arg1, arg2):
    ...     pass
    ...
    >>>

    >>> if myfunc2(2, 1) is not None:
    ...     print("caught")
    ...
    >>> a = 2
    >>> # this is not a block:
"""
expected_lines = expected.split("\n")
expected_labels = {
    1: "none",
    2: "none",
    3: "none",
    4: "none",
    (5, 9): "doctest",
    9: "doctest",
    10: "none",
    11: "none",
    12: "none",
    13: "none",
    14: "none",
    15: "doctest",
    16: "none",
    17: "none",
    (18, 22): "doctest",
    (22, 25): "doctest",
    25: "doctest",
    26: "none",
    (27, 30): "doctest",
    30: "doctest",
    31: "doctest",
    32: "none",
}
expected_line_ranges, expected_line_labels = from_dict(expected_labels)
