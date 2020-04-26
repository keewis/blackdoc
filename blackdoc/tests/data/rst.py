content = """\
Long description of the function's assumptions and on how to call it.

.. note::

    this is not a code block

As an example:

.. code:: python
    :okwarning:

    file = open(
        "very_long_filepath",
        mode="a",
    )


.. code-block:: python

    with open(
        "very_long_filepath",
        mode="a",
    ) as f:
        content = f.read()

A new example, this time with ipython:

.. ipython::

    file = open(
        "very_long_filepath",
        mode="a",
    )
    file

with ipython prompts:

.. ipython::
    :okerror:

    In [1]: file = open(
       ...:     "very_long_filepath",
       ...:     mode="a",
       ...: )

    In [2]: file

    In [3]: file.read_binary()

"""
lines = content.splitlines()
code_units = (1, 1, 9, 9, 1, 9, 1, 12, 1)
line_ranges = (
    (0, 1),
    (1, 2),
    (2, 11),
    (11, 20),
    (20, 21),
    (21, 30),
    (31, 44),
)
line_labels = (
    "none",
    "none",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "none",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "none",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "rst",
    "none",
)
