black-doctest
=============
`black-doctest` is a tool that applies `black` to code in doctest
blocks. It is a rewrite of https://gist.github.com/mattharrison/2a1a263597d80e99cf85e898b800ec32

Usage
-----
There is no commandline interface, yet. Until it is added, use:

.. code:: bash

    # preview
    python -c 'import blackdoc; import pathlib; path = pathlib.Path("file.py"); print(blackdoc.format_file(path))'
    # inplace conversion
    python -c 'import blackdoc; import pathlib; path = pathlib.Path("file.py"); path.write_text(blackdoc.format_file(path))'
