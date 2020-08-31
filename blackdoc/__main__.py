import argparse
import pathlib
import sys

import black

from . import __version__, format_lines, formats
from .blackcompat import gen_python_files


def check_format_names(string):
    names = string.split(",")
    allowed_names = set(formats.detection_funcs.keys()) - set(["none"])
    for name in names:
        if name in allowed_names:
            continue

        raise argparse.ArgumentTypeError(
            f"invalid choice: {name!r} (choose from {', '.join(sorted(allowed_names))})"
        )
    return names


def collect_files(src, include, exclude):
    root = black.find_project_root(tuple(src))
    gitignore = black.get_gitignore(root)
    report = black.Report()

    force_exclude = ""

    for path in src:
        if path.is_dir():
            yield from gen_python_files(
                path.iterdir(),
                root,
                include,
                exclude,
                force_exclude,
                report,
                gitignore,
            )
        elif path.is_file() or str(path) == "-":
            yield path
        else:
            print(f"invalid path: {path}", file=sys.stderr)


def format_and_overwrite(path, mode):
    try:
        with open(path, mode="rb") as f:
            content, encoding, newline = black.decode_bytes(f.read())

        lines = content.split("\n")

        new_content = "\n".join(format_lines(lines, mode))

        if new_content == content:
            result = "unchanged"
        else:
            print(f"reformatted {path}")
            result = "reformatted"

        with open(path, "w", encoding=encoding, newline=newline) as f:
            f.write(new_content)
    except black.InvalidInput as e:
        print(f"error: cannot format {path.absolute()}: {e}")
        result = "error"

    return result


def format_and_check(path, mode):
    try:
        with open(path, mode="rb") as f:
            content, _, _ = black.decode_bytes(f.read())

        lines = content.split("\n")

        new_content = "\n".join(format_lines(lines, mode))

        if new_content == content:
            result = "unchanged"
        else:
            print(f"would reformat {path}")
            result = "reformatted"
    except black.InvalidInput as e:
        print(f"error: cannot format {path.absolute()}: {e}")
        result = "error"

    return result


def report_changes(n_reformatted, n_unchanged, n_error):
    def noun(n):
        return "file" if n < 2 else "files"

    reports = []
    if n_reformatted > 0:
        reports.append(f"{n_reformatted} {noun(n_reformatted)} reformatted")

    if n_unchanged > 0:
        reports.append(f"{n_unchanged} {noun(n_unchanged)} left unchanged")

    if n_error > 0:
        reports.append(f"{n_error} {noun(n_error)} fails to reformat")

    return ", ".join(reports) + "."


def report_possible_changes(n_reformatted, n_unchanged, n_error):
    def noun(n):
        return "file" if n < 2 else "files"

    reports = []
    if n_reformatted > 0:
        reports.append(f"{n_reformatted} {noun(n_reformatted)} would be reformatted")

    if n_unchanged > 0:
        reports.append(f"{n_unchanged} {noun(n_unchanged)} would be left unchanged")

    if n_error > 0:
        reports.append(f"{n_error} {noun(n_error)} would fail to reformat")

    return ", ".join(reports) + "."


def statistics(sources):
    from collections import Counter

    statistics = Counter(sources.values())

    n_unchanged = statistics.pop("unchanged", 0)
    n_reformatted = statistics.pop("reformatted", 0)
    n_error = statistics.pop("error", 0)

    if len(statistics) != 0:
        raise RuntimeError(f"unknown results: {statistics.keys()}")

    return n_reformatted, n_unchanged, n_error


def process(args):
    if not args.src:
        print("No Path provided. Nothing to do 😴")
        return 0

    selected_formats = getattr(args, "formats", None)
    if selected_formats:
        formats.disable(
            set(formats.detection_funcs.keys()) - set(selected_formats) - set(["none"])
        )

    disabled_formats = getattr(args, "disable_formats", None)
    if disabled_formats:
        formats.disable(disabled_formats)

    try:
        include_regex = black.re_compile_maybe_verbose(args.include)
    except black.re.error:
        print(
            f"Invalid regular expression for include given: {args.include!r}",
            file=sys.stderr,
        )
        return 2

    try:
        exclude_regex = black.re_compile_maybe_verbose(args.exclude)
    except black.re.error:
        print(
            f"Invalid regular expression for exclude given: {args.exclude!r}",
            file=sys.stderr,
        )
        return 2

    sources = set(collect_files(args.src, include_regex, exclude_regex))
    if len(sources) == 0:
        print("No files are present to be formatted. Nothing to do 😴")
        return 0

    target_versions = set(
        black.TargetVersion[version.upper()]
        for version in getattr(args, "target_versions", ())
    )
    mode = black.FileMode(
        line_length=args.line_length,
        target_versions=target_versions,
    )

    actions = {
        "inplace": format_and_overwrite,
        "check": format_and_check,
    }

    action = actions.get(args.action)

    changed_sources = {source: action(source, mode) for source in sources}
    n_reformatted, n_unchanged, n_error = statistics(changed_sources)

    report_formatters = {
        "inplace": report_changes,
        "check": report_possible_changes,
    }

    report = report_formatters.get(args.action)(n_reformatted, n_unchanged, n_error)

    if n_error > 0:
        return_code = 123
    elif args.action == "check" and n_reformatted > 0:
        return_code = 1
    else:
        return_code = 0

    print("Oh no! 💥 💔 💥" if return_code else "All done! ✨ 🍰 ✨")
    print(report)
    return return_code


def main():
    program = pathlib.Path(__file__).parent.name

    parser = argparse.ArgumentParser(
        description="run black on documentation code snippets (e.g. doctest)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog=program,
    )
    parser.add_argument(
        "-t",
        "--target-versions",
        action="append",
        choices=[v.name.lower() for v in black.TargetVersion],
        help=(
            "Python versions that should be supported by Black's output. (default: "
            "per-file auto-detection)"
        ),
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-l",
        "--line-length",
        metavar="INT",
        type=int,
        default=black.DEFAULT_LINE_LENGTH,
        help="How many characters per line to allow.",
    )
    parser.add_argument(
        "--check",
        dest="action",
        action="store_const",
        const="check",
        default="inplace",
        help=(
            "Don't write the files back, just return the status.  Return code 0 "
            "means nothing would change.  Return code 1 means some files would be "
            "reformatted.  Return code 123 means there was an internal error."
        ),
    )
    parser.add_argument(
        "--include",
        metavar="TEXT",
        type=str,
        default=formats.format_include_patterns(),
        help=(
            "A regular expression that matches files and directories that should be "
            "included on recursive searches.  An empty value means all files are "
            "included regardless of the name.  Use forward slashes for directories on "
            "all platforms (Windows, too).  Exclusions are calculated first, inclusions "
            "later."
        ),
    )
    parser.add_argument(
        "--exclude",
        metavar="TEXT",
        type=str,
        default=black.DEFAULT_EXCLUDES,
        help=(
            "A regular expression that matches files and directories that should be "
            "excluded on recursive searches.  An empty value means no paths are excluded. "
            "Use forward slashes for directories on all platforms (Windows, too).  "
            "Exclusions are calculated first, inclusions later."
        ),
    )
    parser.add_argument(
        "--formats",
        metavar="FMT[,FMT[,FMT...]]",
        type=check_format_names,
        help="Use only the specified formats.",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--disable-formats",
        metavar="FMT[,FMT[,FMT...]]",
        type=check_format_names,
        help=(
            "Disable the given formats. "
            "This option also affects formats explicitly set."
        ),
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--version",
        action="version",
        help="Show the version and exit.",
        version=f"{program} {__version__}",
    )
    parser.add_argument(
        "src",
        action="store",
        type=pathlib.Path,
        nargs="*",
        default=None,
        help="one or more paths to work on",
    )

    args = parser.parse_args()
    sys.exit(process(args))


if __name__ == "__main__":
    main()
