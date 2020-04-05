content = """\
Long description of the function's assumptions and on how to call it.
As an example:

.. code:: python
    :okwarning:

    file = open(
        "very_long_filepath",
        mode="a",
    )

A new example, this time with ipython:

.. ipython:: python

    file
"""
lines = content.splitlines()
code_units = (1, 1, 1, 7, 1, 1, 1, 3, 1)
line_labels = (
    "none",
    "none",
    "none",
    "rst-codeblock",
    "rst-codeblock",
    "rst-codeblock",
    "rst-codeblock",
    "rst-codeblock",
    "rst-codeblock",
    "rst-codeblock",
    "none",
    "none",
    "none",
    "rst-codeblock",
    "rst-codeblock",
    "rst-codeblock",
    "none",
)
