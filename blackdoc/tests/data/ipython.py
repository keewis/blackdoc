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

    In [4]: %%time
       ...: file.close()

    In [5]: @savefig simple.png width=4in
       ...: @property
       ...: def my_property(self):
       ...:     pass
"""
lines = docstring.split("\n")
code_units = (1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 4, 1)
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
    (18, 20),
    (20, 21),
    (21, 25),
    (25, 26),
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
    "ipython",
    "ipython",
    "none",
    "ipython",
    "ipython",
    "ipython",
    "ipython",
    "none",
)
