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
code_units = (1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1)
line_labels = (
    "none",
    "none",
    "none",
    "none",
    "ipython",
    "ipython",
    "ipython",
    "ipython",
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
