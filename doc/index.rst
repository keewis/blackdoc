blackdoc: apply black to code in documentation
==============================================

**blackdoc** extracts code from documentation, applies **black** to it
and writes it back to the file.

The currently supported formats are:

- doctest
- ipython
- rst

Installation
------------
**blackdoc** depends on

- `black`_
- `more-itertools`_
- `importlib-metadata`_ (on **python** < 3.8)


It has not been released, yet, so use:

.. code:: bash

   python -m pip install git+https://github.com/keewis/blackdoc

for installation.


.. _more-itertools: https://more-itertools.readthedocs.io/
.. _black: https://black.readthedocs.io/en/stable/
.. _importlib-metadata: https://importlib-metadata.readthedocs.io/en/latest/
