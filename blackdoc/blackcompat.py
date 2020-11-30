"""vendored code copied from black

For the license, see /licenses/black
"""

from functools import lru_cache
from pathlib import Path

import toml


@lru_cache()
def find_project_root(srcs):
    """Return a directory containing .git, .hg, or pyproject.toml.

    That directory will be a common parent of all files and directories
    passed in `srcs`.

    If no directory in the tree contains a marker that would specify it's the
    project root, the root of the file system is returned.
    """
    if not srcs:
        return Path("/").resolve()

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
            return directory

        if (directory / ".hg").is_dir():
            return directory

        if (directory / "pyproject.toml").is_file():
            return directory

    return directory


def wrap_stream_for_windows(f):
    """
    Wrap stream with colorama's wrap_stream so colors are shown on Windows.
    If `colorama` is unavailable, the original stream is returned unmodified.
    Otherwise, the `wrap_stream()` function determines whether the stream needs
    to be wrapped for a Windows environment and will accordingly either return
    an `AnsiToWin32` wrapper or the original stream.
    """
    try:
        from colorama.initialise import wrap_stream
    except ImportError:
        return f
    else:
        # Set `strip=False` to avoid needing to modify test_express_diff_with_color.
        return wrap_stream(f, convert=None, strip=False, autoreset=False, wrap=True)


def find_pyproject_toml(path_search_start):
    """Find the absolute filepath to a pyproject.toml if it exists"""
    path_project_root = find_project_root(path_search_start)
    path_pyproject_toml = path_project_root / "pyproject.toml"
    return str(path_pyproject_toml) if path_pyproject_toml.is_file() else None


def parse_pyproject_toml(path_config):
    """Parse a pyproject toml file, pulling out relevant parts for Black

    If parsing fails, will raise a toml.TomlDecodeError
    """
    pyproject_toml = toml.load(path_config)
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
    except (toml.TomlDecodeError, OSError) as e:
        raise IOError(f"Error reading configuration file ({config_path}): {e}")

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


def gen_python_files(paths, root, include, exclude, force_exclude, report, gitignore):
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

        # First ignore files matching .gitignore
        if gitignore.match_file(normalized_path):
            report.path_ignored(child, "matches the .gitignore file content")
            continue

        # Then ignore with `--exclude` and `--force-exclude` options.
        normalized_path = "/" + normalized_path
        if child.is_dir():
            normalized_path += "/"

        exclude_match = exclude.search(normalized_path) if exclude else None
        if exclude_match and exclude_match.group(0):
            report.path_ignored(child, "matches the --exclude regular expression")
            continue

        force_exclude_match = (
            force_exclude.search(normalized_path) if force_exclude else None
        )
        if force_exclude_match and force_exclude_match.group(0):
            report.path_ignored(child, "matches the --force-exclude regular expression")
            continue

        if child.is_dir():
            yield from gen_python_files(
                child.iterdir(),
                root,
                include,
                exclude,
                force_exclude,
                report,
                gitignore,
            )

        elif child.is_file():
            include_match = include.search(normalized_path) if include else True
            if include_match:
                yield child
