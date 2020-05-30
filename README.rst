blackdoc
========

.. image:: https://github.com/keewis/blackdoc/workflows/CI/badge.svg?branch=master
    :target: https://github.com/keewis/blackdoc/actions
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/python/black
.. image:: https://readthedocs.org/projects/blackdoc/badge/?version=latest
    :target: https://blackdoc.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

**blackdoc** is a tool that applies `black`_ to code in documentation.

It was originally a rewrite of a `gist`_ and called
**black-doctest**. In April 2020, it was renamed to **blackdoc**.

.. _gist: https://gist.github.com/mattharrison/2a1a263597d80e99cf85e898b800ec32
.. _black: https://github.com/psf/black

Installation
------------
Dependencies:

- `black`_
- `more-itertools`_

.. _more-itertools: https://github.com/more-itertools/more-itertools

Install it with:

.. code:: bash

    python -m pip install blackdoc

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

It is also possible to use the entrypoint script:

.. code:: bash

    blackdoc --help
