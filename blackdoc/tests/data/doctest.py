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
}
line_ranges = tuple(
    (lineno - 1, lineno)
    if not isinstance(lineno, tuple)
    else tuple(n - 1 for n in lineno)
    for lineno in labels.keys()
)
line_labels = labels.values()
