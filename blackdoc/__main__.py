import argparse
import datetime
import difflib
import functools
import pathlib
import re
import sys

import black

from . import __version__, format_lines, formats
from .blackcompat import (
    find_project_root,
    gen_python_files,
    read_pyproject_toml,
    wrap_stream_for_windows,
)

colors_re = re.compile("\033" + r"\[[0-9]+(?:;[0-9]+)*m")


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


def collect_files(src, include, exclude, force_exclude):
    root = find_project_root(tuple(src))
    gitignore = black.get_gitignore(root)
    report = black.Report()

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
        elif str(path) == "-":
            yield path
        elif path.is_file():
            normalized_path = black.normalize_path_maybe_ignore(path, root, report)
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
            print(f"invalid path: {path}", file=sys.stderr)


def colorize(string, fg=None, bold=False):
    foreground_colors = {
        "white": 37,
        "cyan": 36,
        "green": 32,
        "red": 31,
    }
    bold_code = 1
    reset_code = 0

    codes = []
    if bold:
        codes.append(bold_code)

    if fg:
        codes.append(foreground_colors.get(fg, fg))

    return f"\033[{';'.join(map(str, codes))}m{string}\033[{reset_code}m"


def remove_colors(message):
    return "".join(colors_re.split(message))


# signature inspired by click.secho
def custom_print(message, end="\n", file=sys.stdout, **styles):
    if file.isatty():
        message = colorize(message, **styles)
    else:
        message = remove_colors(message)

    print(message, end=end, file=wrap_stream_for_windows(file))


out = functools.partial(custom_print, file=sys.stdout)
err = functools.partial(custom_print, file=sys.stderr)


def color_diff(contents):
    """Inject the ANSI color codes to the diff."""
    lines = contents.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("+++") or line.startswith("---"):
            line = colorize(line, fg="white", bold=True)  # bold white, reset
        elif line.startswith("@@"):
            line = colorize(line, fg="cyan")  # cyan, reset
        elif line.startswith("+"):
            line = colorize(line, fg="green")  # green, reset
        elif line.startswith("-"):
            line = colorize(line, fg="red")  # red, reset
        lines[i] = line
    return "\n".join(lines)


def unified_diff(a, b, path, color):
    then = datetime.datetime.utcfromtimestamp(path.stat().st_mtime)
    now = datetime.datetime.utcnow()
    src_name = f"{path}\t{then} +0000"
    dst_name = f"{path}\t{now} +0000"

    diff = "\n".join(
        difflib.unified_diff(
            a.splitlines(),
            b.splitlines(),
            fromfile=src_name,
            tofile=dst_name,
            lineterm="",
        )
    )
    if color:
        diff = color_diff(diff)

    return diff


def format_and_overwrite(path, mode):
    try:
        with open(path, mode="rb") as f:
            content, encoding, newline = black.decode_bytes(f.read())

        lines = content.split("\n")

        new_content = "\n".join(format_lines(lines, mode))

        if new_content == content:
            result = "unchanged"
        else:
            err(f"reformatted {path}", fg="white", bold=True)
            result = "reformatted"

        with open(path, "w", encoding=encoding, newline=newline) as f:
            f.write(new_content)
    except black.InvalidInput as e:
        err(f"error: cannot format {path.absolute()}: {e}", fg="red")
        result = "error"

    return result


def format_and_check(path, mode, diff=False, color=False):
    try:
        with open(path, mode="rb") as f:
            content, _, _ = black.decode_bytes(f.read())

        lines = content.split("\n")

        new_content = "\n".join(format_lines(lines, mode))

        if new_content == content:
            result = "unchanged"
        else:
            err(f"would reformat {path}", fg="white", bold=True)

            if diff:
                out(unified_diff(content, new_content, path, color))

            result = "reformatted"
    except black.InvalidInput as e:
        err(f"error: cannot format {path.absolute()}: {e}", fg="red")
        result = "error"

    return result


def report_changes(n_reformatted, n_unchanged, n_error):
    def noun(n):
        return "file" if n < 2 else "files"

    reports = []
    if n_reformatted > 0:
        reports.append(
            colorize(
                f"{n_reformatted} {noun(n_reformatted)} reformatted",
                fg="white",
                bold=True,
            )
        )

    if n_unchanged > 0:
        reports.append(
            colorize(f"{n_unchanged} {noun(n_unchanged)} left unchanged", fg="white")
        )

    if n_error > 0:
        reports.append(
            colorize(f"{n_error} {noun(n_error)} fails to reformat", fg="red")
        )

    return ", ".join(reports) + "."


def report_possible_changes(n_reformatted, n_unchanged, n_error):
    def noun(n):
        return "file" if n < 2 else "files"

    reports = []
    if n_reformatted > 0:
        reports.append(
            colorize(
                f"{n_reformatted} {noun(n_reformatted)} would be reformatted",
                fg="white",
                bold=True,
            )
        )

    if n_unchanged > 0:
        reports.append(
            colorize(
                f"{n_unchanged} {noun(n_unchanged)} would be left unchanged", fg="white"
            )
        )

    if n_error > 0:
        reports.append(
            colorize(f"{n_error} {noun(n_error)} would fail to reformat", fg="red")
        )

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
        err("No Path provided. Nothing to do 😴", fg="white", bold=True)
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
        err(f"Invalid regular expression for include given: {args.include!r}", fg="red")
        return 2

    try:
        exclude_regex = black.re_compile_maybe_verbose(args.exclude)
    except black.re.error:
        err(f"Invalid regular expression for exclude given: {args.exclude!r}", fg="red")
        return 2

    try:
        force_exclude = getattr(args, "force_exclude", "")
        force_exclude_regex = (
            black.re_compile_maybe_verbose(force_exclude) if force_exclude else None
        )
    except black.re.error:
        err(
            f"Invalid regular expression for force_exclude given: {force_exclude!r}",
            fg="red",
        )
        return 2

    sources = set(
        collect_files(args.src, include_regex, exclude_regex, force_exclude_regex)
    )
    if len(sources) == 0:
        err(
            "No files are present to be formatted. Nothing to do 😴",
            fg="white",
            bold=True,
        )
        return 0

    target_versions = set(
        black.TargetVersion[version.upper()]
        for version in getattr(args, "target_versions", ())
    )
    mode = black.FileMode(
        line_length=args.line_length,
        target_versions=target_versions,
        string_normalization=not args.skip_string_normalization,
    )

    actions = {
        "inplace": format_and_overwrite,
        "check": format_and_check,
    }
    action_kwargs = {"diff": args.diff, "color": args.color} if args.diff else {}

    action = actions.get(args.action)

    changed_sources = {
        source: action(source, mode, **action_kwargs) for source in sorted(sources)
    }
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

    reformatted_message = "Oh no! 💥 💔 💥"
    no_reformatting_message = "All done! ✨ 🍰 ✨"
    err(
        reformatted_message if return_code else no_reformatting_message,
        fg="white",
        bold=True,
    )
    err(report)
    return return_code


class boolean_flag(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super().__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        value = False if option_string.startswith("--no-") else True
        setattr(namespace, self.dest, value)


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
        "--diff",
        dest="diff",
        action="store_const",
        const="diff",
        help="Don't write the files back, just output a diff for each file on stdout.",
    )
    parser.add_argument(
        "--color",
        "--no-color",
        dest="color",
        action=boolean_flag,
        default=False,
        help="Show colored diff. Only applies when `--diff` is given.",
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
        "--force-exclude",
        metavar="TEXT",
        type=str,
        default=argparse.SUPPRESS,
        help=(
            "Like --exclude, but files and directories"
            " matching this regex will be excluded even"
            " when they are passed explicitly as arguments"
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
        "-S",
        "--skip-string-normalization",
        dest="skip_string_normalization",
        action="store_true",
        help="Don't normalize string quotes or prefixes.",
    )
    parser.add_argument(
        "--version",
        action="version",
        help="Show the version and exit.",
        version=f"{program} {__version__}",
    )
    parser.add_argument(
        "--config",
        action="store",
        nargs=1,
        type=pathlib.Path,
        default=None,
        help="Read configuration from FILE path.",
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
    if args.config or args.src:
        file_defaults = read_pyproject_toml(tuple(args.src), args.config)
        parser.set_defaults(**file_defaults)

    if args.diff:
        parser.set_defaults(action="check")

    args = parser.parse_args()
    sys.exit(process(args))


if __name__ == "__main__":
    main()
