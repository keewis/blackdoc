"""vendored code copied from black

For the license, see /licenses/black
"""

import pathlib
from distutils.version import LooseVersion

import black

if LooseVersion(black.__version__) >= LooseVersion("20.08b0"):
    from black import gen_python_files
else:

    def normalize_path_maybe_ignore(path, root, report):
        """Normalize `path`. May return `None` if `path` was ignored.
        `report` is where "path ignored" output goes.
        """
        try:
            abspath = path if path.is_absolute() else pathlib.Path.cwd() / path
            normalized_path = abspath.resolve().relative_to(root).as_posix()
        except OSError as e:
            report.path_ignored(path, f"cannot be read because {e}")
            return None

        except ValueError:
            if path.is_symlink():
                report.path_ignored(
                    path, f"is a symbolic link that points outside {root}"
                )
                return None

            raise

        return normalized_path

    def gen_python_files(
        paths, root, include, exclude, force_exclude, report, gitignore
    ):
        """Generate all files under `path` whose paths are not excluded by the
        `exclude_regex` or `force_exclude` regexes, but are included by the `include` regex.

        Symbolic links pointing outside of the `root` directory are ignored.

        `report` is where output about exclusions goes.
        """
        assert (
            root.is_absolute()
        ), f"INTERNAL ERROR: `root` must be absolute but is {root}"
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
                report.path_ignored(
                    child, "matches the --force-exclude regular expression"
                )
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
