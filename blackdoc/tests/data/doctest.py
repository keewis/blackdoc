from . import from_dict

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

    >>> def myfunc2(arg1, arg2):
    ...     '''Docstring for function myfunc2 in docstring
    ...
    ...     More description of the function.
    ...     '''
    ...     pass
    >>>

    >>> if myfunc2(2, 1) is not None:
    ...     print("caught")
    >>> a = 2
    ...
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
    (18, 24): "doctest",
    24: "doctest",
    25: "none",
    (26, 28): "doctest",
    (28, 30): "doctest",
    30: "none",
}
line_ranges, line_labels = from_dict(labels)
