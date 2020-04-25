docstring = """ a function to open files

    with a very long description

    In [1]: file = open(
       ...:    "very_long_filepath",
       ...:    mode="a",
       ...: )

    In [2]: file
    Out[2]: <_io.TextIOWrapper name='very_long_filepath' mode='w' encoding='UTF-8'>

    text after the first example, spanning
    multiple lines

    In [3]: file.closed
    Out[3]: False
"""
lines = docstring.split("\n")
code_units = (1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
line_ranges = (
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 8),
    (8, 9),
    (9, 10),
    (10, 11),
    (11, 12),
    (12, 13),
    (13, 14),
    (14, 15),
    (15, 16),
    (16, 17),
    (17, 18),
)
line_labels = (
    "none",
    "none",
    "none",
    "none",
    "ipython",
    "ipython",
    "ipython",
    "ipython",
    "none",
    "ipython",
    "none",
    "none",
    "none",
    "none",
    "none",
    "ipython",
    "none",
    "none",
)
