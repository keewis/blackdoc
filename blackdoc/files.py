from black import Report

from blackdoc.blackcompat import (
    find_project_root,
    gen_python_files,
    get_gitignore,
    normalize_path_maybe_ignore,
)
from blackdoc.console import err


def collect_files(src, include, exclude, extend_exclude, force_exclude, quiet, verbose):
    root, _ = find_project_root(tuple(src))
    gitignore = get_gitignore(root)
    report = Report()

    for path in src:
        if path.is_dir():
            yield from gen_python_files(
                path.iterdir(),
                root,
                include,
                exclude,
                extend_exclude,
                force_exclude,
                report,
                gitignore,
                quiet=quiet,
                verbose=verbose,
            )
        elif str(path) == "-":
            yield path
        elif path.is_file():
            normalized_path = normalize_path_maybe_ignore(path, root, report)
            if normalized_path is None:
                continue

            normalized_path = "/" + normalized_path
            # Hard-exclude any files that matches the `--force-exclude` regex.
            if force_exclude:
                force_exclude_match = force_exclude.search(normalized_path)
            else:
                force_exclude_match = None
            if force_exclude_match and force_exclude_match.group(0):
                report.path_ignored(
                    path, "matches the --force-exclude regular expression"
                )
                continue

            yield path
        else:
            err.print(f"invalid path: {path}", style="red")
