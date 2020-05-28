.. directory/file.rst
file with code:

.. code:: python

    def function_with_long_name(
        parameter1, parameter2, parameter3, *variable_args, **keyword_args
    ):
        pass

more code:

.. code-block:: python

    for index, (value1, value2, value3, value4) in enumerate(
        zip(iterable1, iterable2, iterable3, iterable4)
    ):
        pass

executed code:

.. ipython:: python

    keys = ("key1", "key2")
    values = (15, 4)

    mapping = dict(zip(keys, values))

    mapping

with explicit grouping:

.. ipython:: python

    In [1]: keys = ("key1", "key2")
       ...: values = {15, 4}

    In [2]: mapping = {key: value for key, value in zip(keys, values)}
       ...: mapping
