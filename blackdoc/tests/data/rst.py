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
lines = content.splitlines()
line_ranges = (
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 8),
    (8, 15),
    (15, 16),
    (16, 17),
    (17, 24),
    (24, 25),
    (25, 26),
    (26, 27),
    (27, 35),
    (35, 36),
    (36, 37),
    (37, 38),
    (38, 39),
    (39, 40),
    (40, 41),
    (41, 42),
    (42, 43),
    (43, 44),
    (44, 45),
    (45, 46),
    (46, 47),
    (47, 48),
    (48, 49),
    (49, 50),
    (50, 51),
    (51, 52),
    (52, 53),
    (53, 54),
    (54, 55),
    (55, 56),
    (56, 57),
    (57, 58),
    (58, 59),
    (59, 60),
    (60, 61),
    (61, 62),
    (62, 63),
    (63, 64),
    (64, 65),
    (65, 66),
    (66, 67),
    (67, 70),
    (70, 71),
    (71, 72),
    (72, 73),
    (73, 74),
    (74, 75),
    (75, 76),
    (76, 77),
    (77, 78),
    (78, 79),
    (79, 80),
    (80, 81),
    (81, 82),
    (82, 83),
    (83, 84),
    (84, 85),
    (85, 86),
    (86, 87),
)
line_labels = (
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "rst",
    "none",
    "none",
    "rst",
    "none",
    "none",
    "none",
    "rst",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
    "none",
)
