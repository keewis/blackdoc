from blackdoc.tests.data.utils import from_dict

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
labels = {
    1: "none",
    2: "none",
    3: "none",
    4: "none",
    (5, 9): "ipython",
    9: "none",
    10: "ipython",
    11: "none",
    12: "none",
    13: "none",
    14: "none",
    15: "none",
    16: "ipython",
    17: "none",
    18: "none",
    (19, 21): "ipython",
    21: "none",
    (22, 26): "ipython",
    26: "none",
}
line_ranges, line_labels = from_dict(labels)
