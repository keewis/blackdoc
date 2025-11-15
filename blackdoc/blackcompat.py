"""vendored code copied from black

For the license, see /licenses/black
"""

import io
import os
import sys
from functools import lru_cache
from pathlib import Path

import tomli
from black import Encoding, FileContent, Mode, NewLine, Preview, tokenize
from pathspec import PathSpec


@lru_cache
def find_project_root(srcs):
    """Return a directory containing .git, .hg, or pyproject.toml.

    That directory will be a common parent of all files and directories
    passed in `srcs`.

    If no directory in the tree contains a marker that would specify it's the
    project root, the root of the file system is returned.

    Returns a two-tuple with the first element as the project root path and
    the second element as a string describing the method by which the
    project root was discovered.
    """
    if not srcs:
        srcs = [str(Path.cwd().resolve())]

    path_srcs = [Path(Path.cwd(), src).resolve() for src in srcs]

    # A list of lists of parents for each 'src'. 'src' is included as a
    # "parent" of itself if it is a directory
    src_parents = [
        list(path.parents) + ([path] if path.is_dir() else []) for path in path_srcs
    ]

    common_base = max(
        set.intersection(*(set(parents) for parents in src_parents)),
        key=lambda path: path.parts,
    )

    for directory in (common_base, *common_base.parents):
        if (directory / ".git").exists():
            return directory, ".git directory"

        if (directory / ".hg").is_dir():
            return directory, ".hgdirectory"

        if (directory / "pyproject.toml").is_file():
            return directory, "pyproject.toml"

    return directory, "file system root"


def find_pyproject_toml(path_search_start):
    """Find the absolute filepath to a pyproject.toml if it exists"""
    path_project_root, _ = find_project_root(path_search_start)
    path_pyproject_toml = path_project_root / "pyproject.toml"
    if path_pyproject_toml.is_file():
        return str(path_pyproject_toml)

    try:
        path_user_pyproject_toml = find_user_pyproject_toml()
        return (
            str(path_user_pyproject_toml)
            if path_user_pyproject_toml.is_file()
            else None
        )
    except (PermissionError, RuntimeError) as e:
        # We do not have access to the user-level config directory, so ignore it.
        print(f"Ignoring user configuration directory due to {e!r}")
        return None


@lru_cache
def find_user_pyproject_toml():
    r"""Return the path to the top-level user configuration for black.

    This looks for ~\.black on Windows and ~/.config/black on Linux and other
    Unix systems.

    May raise:
    - RuntimeError: if the current user has no homedir
    - PermissionError: if the current process cannot access the user's homedir
    """
    if sys.platform == "win32":
        # Windows
        user_config_path = Path.home() / ".black"
    else:
        config_root = os.environ.get("XDG_CONFIG_HOME", "~/.config")
        user_config_path = Path(config_root).expanduser() / "black"
    return user_config_path.resolve()


def parse_pyproject_toml(path_config):
    """Parse a pyproject toml file, pulling out relevant parts for Black and Blackdoc

    If parsing fails, will raise a tomli.TOMLDecodeError
    """
    with open(path_config, "rb") as f:
        pyproject_toml = tomli.load(f)

    black_config = pyproject_toml.get("tool", {}).get("black", {})
    blackdoc_config = pyproject_toml.get("tool", {}).get("blackdoc", {})
    config = {**black_config, **blackdoc_config}

    return {k.replace("--", "").replace("-", "_"): v for k, v in config.items()}


def read_pyproject_toml(source, config_path):
    if not config_path:
        config_path = find_pyproject_toml(source)
        if config_path is None:
            return {}

    try:
        config = parse_pyproject_toml(config_path)
    except (ValueError, OSError) as e:
        raise OSError(
            f"Error reading configuration file ({config_path}): {e}"
        ) from None

    if not config:
        return {}

    return config


def normalize_path_maybe_ignore(path, root, report):
    """Normalize `path`. May return `None` if `path` was ignored.

    `report` is where "path ignored" output goes.
    """
    try:
        abspath = path if path.is_absolute() else Path.cwd() / path
        normalized_path = abspath.resolve().relative_to(root).as_posix()
    except OSError as e:
        report.path_ignored(path, f"cannot be read because {e}")
        return None

    except ValueError:
        if path.is_symlink():
            report.path_ignored(path, f"is a symbolic link that points outside {root}")
            return None

        raise

    return normalized_path


def path_is_excluded(normalized_path, pattern):
    match = pattern.search(normalized_path) if pattern else None
    return bool(match and match.group(0))


@lru_cache
def get_gitignore(root):
    """Return a PathSpec matching gitignore content if present."""
    gitignore = root / ".gitignore"
    lines = []
    if gitignore.is_file():
        with gitignore.open(encoding="utf-8") as gf:
            lines = gf.readlines()
    return PathSpec.from_lines("gitwildmatch", lines)


@lru_cache
def jupyter_dependencies_are_installed(*, verbose, quiet):
    try:
        import IPython  # noqa:F401
        import tokenize_rt  # noqa:F401
    except ModuleNotFoundError:
        if verbose or not quiet:
            msg = (
                "Skipping .ipynb files as Jupyter dependencies are not installed.\n"
                "You can fix this by running ``pip install black[jupyter]``"
            )
            print(msg)
        return False
    else:
        return True


def gen_python_files(
    paths,
    root,
    include,
    exclude,
    extend_exclude,
    force_exclude,
    report,
    gitignore,
    *,
    verbose,
    quiet,
):
    """Generate all files under `path` whose paths are not excluded by the
    `exclude_regex` or `force_exclude` regexes, but are included by the `include` regex.

    Symbolic links pointing outside of the `root` directory are ignored.

    `report` is where output about exclusions goes.
    """
    assert root.is_absolute(), f"INTERNAL ERROR: `root` must be absolute but is {root}"
    for child in paths:
        normalized_path = normalize_path_maybe_ignore(child, root, report)
        if normalized_path is None:
            continue

        # First ignore files matching .gitignore, if passed
        if gitignore is not None and gitignore.match_file(normalized_path):
            report.path_ignored(child, "matches the .gitignore file content")
            continue

        # Then ignore with `--exclude` `--exent-exclude` and `--force-exclude` options.
        normalized_path = "/" + normalized_path
        if child.is_dir():
            normalized_path += "/"

        if path_is_excluded(normalized_path, exclude):
            report.path_ignored(child, "matches the --exclude regular expression")
            continue

        if path_is_excluded(normalized_path, extend_exclude):
            report.path_ignored(
                child, "matches the --extend-exclude regular expression"
            )
            continue

        if path_is_excluded(normalized_path, force_exclude):
            report.path_ignored(child, "matches the --force-exclude regular expression")
            continue

        if child.is_dir():
            # If gitignore is None, gitignore usage is disabled, while a Falsey
            # gitignore is when the directory doesn't have a .gitignore file.
            yield from gen_python_files(
                child.iterdir(),
                root,
                include,
                exclude,
                extend_exclude,
                force_exclude,
                report,
                gitignore + get_gitignore(child) if gitignore is not None else None,
                verbose=verbose,
                quiet=quiet,
            )

        elif child.is_file():
            # if child.suffix == ".ipynb" and not jupyter_dependencies_are_installed(
            #     verbose=verbose, quiet=quiet
            # ):
            #     continue
            include_match = include.search(normalized_path) if include else True
            if include_match:
                yield child


def decode_bytes(src: bytes, mode: Mode) -> tuple[FileContent, Encoding, NewLine]:
    """Return a tuple of (decoded_contents, encoding, newline).

    `newline` is either CRLF or LF but `decoded_contents` is decoded with
    universal newlines (i.e. only contains LF).
    """
    srcbuf = io.BytesIO(src)
    encoding, lines = tokenize.detect_encoding(srcbuf.readline)
    if not lines:
        return "", encoding, "\n"

    normalize_cr_newlines = getattr(Preview, "normalize_cr_newlines", None)
    # by default disabled
    if normalize_cr_newlines is not None and normalize_cr_newlines in mode:
        if lines[0][-2:] == b"\r\n":
            if b"\r" in lines[0][:-2]:
                newline = "\r"
            else:
                newline = "\r\n"
        elif lines[0][-1:] == b"\n":
            if b"\r" in lines[0][:-1]:
                newline = "\r"
            else:
                newline = "\n"
        else:
            if b"\r" in lines[0]:
                newline = "\r"
            else:
                newline = "\n"
    else:
        newline = "\r\n" if lines[0][-2:] == b"\r\n" else "\n"

    srcbuf.seek(0)
    with io.TextIOWrapper(srcbuf, encoding) as tiow:
        return tiow.read(), encoding, newline
