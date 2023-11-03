Usage
=====
command-line interface
----------------------
**blackdoc** tries to copy as much of the CLI of **black** as
possible. This means that most calls to **black** can be directly
translated to **blackdoc**:

To reformat specific files, use:

.. code:: sh

   python -m blackdoc file1 file2 ...

while passing directories reformats all files in those directories
that match the file format specified by ``--include`` and
``--exclude``:

.. code:: sh

   python -m blackdoc directory1 directory2 ...

mixing directories and files is also possible.

As an example, having a structure like::

    directory
    ├── file.py
    └── file.rst

with

.. literalinclude:: directory/file.py

.. literalinclude:: directory/file.rst
   :language: rst

If we run

.. code:: sh

    python -m blackdoc directory

we get

.. literalinclude:: directory/reformatted.py

.. literalinclude:: directory/reformatted.rst
   :language: rst

If instead we run

.. code:: sh

    python -m blackdoc --check directory

the result is::

    would reformat directory/file.rst
    would reformat directory/file.py
    Oh no! 💥 💔 💥
    2 files would be reformatted.

with a non-zero exit status.

pre-commit
----------
The repository also defines a ``pre-commit`` hook:

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
