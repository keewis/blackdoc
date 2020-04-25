blackdoc
========

.. image:: https://github.com/keewis/blackdoc/workflows/CI/badge.svg?branch=master
    :target: https://github.com/keewis/blackdoc/actions
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/python/black

`blackdoc` is a tool that applies `black` to code in documentation.

It was originally a rewrite of a
`gist <https://gist.github.com/mattharrison/2a1a263597d80e99cf85e898b800ec32>`_
under the name `black-doctest`. It was renamed to `black-doctest` in
April 2020.

Usage
-----
The commandline interface supports two modes: checking and inplace
reformatting.

.. code:: bash

    python -m blackdoc --help


In inplace reformatting mode, it will reformat the doctest lines and
write them back to disk:

.. code:: bash

    # on explicitly mentioned files
    python -m blackdoc file1.py file2.py
    # on the whole directory
    python -m blackdoc .


When checking, it will report the changed files but will not write them to disk:

.. code:: bash

    python -m blackdoc --check .
