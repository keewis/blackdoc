from blackdoc.tests.data.utils import from_dict

content = """\
Long description of the function's assumptions and on how to call it.

.. note::

    this is not a code block

As an example:

.. code:: python
   :okwarning:

   file = open(
       "very_long_filepath",
       mode="a"
   )


.. code-block:: python

    with open(
        "very_long_filepath",
        mode="a"
    ) as f:
        content = f.read()

A new example, this time with ipython:

.. ipython::

    %%time
    file = open(
        "very_long_filepath",
        mode="a"
    )
    file

with ipython prompts:

.. ipython::
    :okerror:

    In [1]: file = open(
       ...:     "very_long_filepath",
       ...:     mode="a"
       ...: )

    In [2]: file

    In [3]: file.read_binary()

with cell decorator:

.. ipython::
    :okerror:

    @verbatim
    In [1]: file = open(
       ...:     "very_long_filepath",
       ...:     mode="a"
       ...: )

    In [2]: file

    In [3]: file.read_binary()

a code block with a different language:

.. code:: sh

    find . -name "*.py"

a code block with testcode:

.. testsetup::

    file = open(
        "very_long_filepath",
        mode="a"
    )

.. testcode::

    file

.. testcleanup::

    file.close()
"""
lines = content.split("\n")
labels = {
    1: "none",
    2: "none",
    3: "none",
    4: "none",
    5: "none",
    6: "none",
    7: "none",
    8: "none",
    (9, 16): "rst",
    16: "none",
    17: "none",
    (18, 25): "rst",
    25: "none",
    26: "none",
    27: "none",
    (28, 36): "rst",
    36: "none",
    37: "none",
    38: "none",
    39: "none",
    40: "none",
    41: "none",
    42: "none",
    43: "none",
    44: "none",
    45: "none",
    46: "none",
    47: "none",
    48: "none",
    49: "none",
    50: "none",
    51: "none",
    52: "none",
    53: "none",
    54: "none",
    55: "none",
    56: "none",
    57: "none",
    58: "none",
    59: "none",
    60: "none",
    61: "none",
    62: "none",
    63: "none",
    64: "none",
    65: "none",
    66: "none",
    67: "none",
    68: "none",
    69: "none",
    70: "none",
    71: "none",
    72: "none",
    73: "none",
    (74, 80): "rst",
    80: "none",
    (81, 84): "rst",
    84: "none",
    (85, 88): "rst",
    88: "none",
}
line_ranges, line_labels = from_dict(labels)
