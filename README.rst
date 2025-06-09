blackdoc
========

.. image:: https://github.com/keewis/blackdoc/actions/workflows/ci.yml/badge.svg?branch=main
    :target: https://github.com/keewis/blackdoc/actions/workflows/ci.yml
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
- `rich`_
- `tomli`_
- `pathspec`_

.. _more-itertools: https://github.com/more-itertools/more-itertools
.. _rich: https://github.com/textualize/rich
.. _tomli: https://github.com/hukkin/tomli
.. _pathspec: https://github.com/cpburnz/python-pathspec

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

pre-commit
----------
This repository defines a ``pre-commit`` hook:

.. code:: yaml

   hooks:
   ...
   - repo: https://github.com/keewis/blackdoc
     rev: 3.8.0
     hooks:
     - id: blackdoc

It is recommended to *pin* ``black`` in order to avoid having different versions for each contributor. To automatically synchronize this pin with the version of the ``black`` hook, use the ``blackdoc-autoupdate-black`` hook:

.. code:: yaml

   hooks:
   ...
   - repo: https://github.com/psf/black
     rev: 23.10.1
     hooks:
     - id: black
   ...
   - repo: https://github.com/keewis/blackdoc
     rev: 3.8.0
     hooks:
     - id: blackdoc
       additional_dependencies: ["black==23.10.1"]
     - id: blackdoc-autoupdate-black

Note that this hook is *not* run on ``pre-commit autoupdate``.
