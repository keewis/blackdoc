Options
=======
Since it builds on ``black``, ``blackdoc`` supports most options provided by
``black``, in addition to selecting the available formats.

Options can be set using either command line options or a configuration file in
``toml`` format (by default, ``pyproject.toml``).

General options
---------------
These are command line-only options.

custom configuration file
    Using the ``--config`` option, a arbitrary file in ``toml`` format can be
    specified to use instead of ``pyproject.toml``.

check
    With ``--check``, the program will not write back to disk, but instead
    return ``0`` if no file would be changed, ``1`` if a file would be
    reformatted and ``123`` if an internal error occurred.

diff
    In addition to the behavior of ``--check``, ``--diff`` will output a unified diff of
    the changes that would have been made.

color / no-color
    Has no effect without ``--diff``. If enabled, the unified diffs will be colored.

version
    Print the version and exit.

``black``
---------
target_versions
    ``-t`` or ``--target-versions``, ``str``. A comma-separated string of python versions
    (format: ``pyXY``, e.g. ``py38``). By default, the version is auto-detected
    per file.

line_length
    ``-l`` or ``--line-length``, ``int``. How many characters per line to allow. By
    default, set to 88.

skip_string_normalization
    ``-S`` or ``--skip-string-normalization``. If enabled, skips the string normalization.

include
    ``--include``, ``str``. A regular expression that matches files and
    directories that should be included on recursive searches. An empty value
    means all files are included regardless of the name. Use forward slashes for
    directories on all platforms (Windows, too). Exclusions are calculated
    first, inclusions later. By default, set to ``(\.pyi?$|\.rst$)``

exclude
    ``--exclude``, ``str``. A regular expression that matches files and
    directories that should be excluded on recursive searches. An empty value
    means no paths are excluded. Use forward slashes for directories on all
    platforms (Windows, too). Exclusions are calculated first, inclusions
    later. By default, set to
    ``/(\.direnv|\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|\.svn|_build|buck-out|build|dist)/``.

force_exclude
    ``--force-exclude``, ``str``. Like ``--exclude``, but files and directories
    matching this regex will be excluded even when they are passed explicitly as
    arguments. By default, set to ``""``.

``blackdoc``
------------
formats
    ``--formats``, ``str``. A comma-separated string of formats to use. By
    default, all formats are used.

disable_formats
    ``--disable-formats``, ``str``. A comma-separated string of formats not to
    use. This affects even formats that were explicitly enabled. By default, no
    format is disabled.
