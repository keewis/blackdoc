Contributing
============

``blackdoc`` uses several tools to ensure consistency (this is enforced using CI):

- `black`_ for standardized code formatting
- `flake8`_ for code quality
- `isort`_ for standardized ordering of imports

To avoid having to remember to manually run these tools before committing, using
`pre-commit`_ is possible. After installing, enable it using

.. code:: sh

   python -m pip install pre-commit
   # or
   conda install -c conda-forge pre-commit

   pre-commit install

When modifying the test data in ``blackdoc/tests/data/format.py``, make sure the ranges are
correct using

.. code:: sh

   python -m blackdoc.tests.data format

where ``format`` is a placeholder for the name of one of the supported formats.


.. _black: https://black.readthedocs.io/en/stable/
.. _flake8: https://flake8.pycqa.org/en/stable/
.. _isort: https://pycqa.github.io/isort/
.. _pre-commit: https://pre-commit.com/
