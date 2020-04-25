black-doctest
=============

.. image:: https://github.com/keewis/black-doctest/workflows/CI/badge.svg?branch=master
  :target: https://github.com/keewis/black-doctest/actions

`black-doctest` is a tool that applies `black` to code in doctest
blocks. It is a rewrite of https://gist.github.com/mattharrison/2a1a263597d80e99cf85e898b800ec32

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
