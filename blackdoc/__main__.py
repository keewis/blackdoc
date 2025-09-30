import argparse
import pathlib
import sys

import black
from rich.text import Text

from blackdoc import __version__, format_lines, formats
from blackdoc.blackcompat import decode_bytes, read_pyproject_toml
from blackdoc.colors import DiffHighlighter
from blackdoc.console import err, out
from blackdoc.diff import unified_diff
from blackdoc.files import collect_files
from blackdoc.report import Report

diff_highlighter = DiffHighlighter()


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


def format_and_overwrite(path, mode):
    try:
        with open(path, mode="rb") as f:
            content, encoding, newline = decode_bytes(f.read(), mode)

        lines = content.split("\n")

        new_content = "\n".join(format_lines(lines, mode))

        if new_content == content:
            result = "unchanged"
        else:
            err.print(f"reformatted {path}", style="bold", highlight=False)
            result = "reformatted"

            with open(path, "w", encoding=encoding, newline=newline) as f:
                f.write(new_content)
    except (black.InvalidInput, formats.InvalidFormatError) as e:
        err.print(
            f"error: cannot format {path.absolute()}: {e}", style="red", highlight=False
        )
        result = "error"

    return result


def format_and_check(path, mode, diff=False, color=False):
    try:
        with open(path, mode="rb") as f:
            content, _, _ = decode_bytes(f.read(), mode)

        lines = content.split("\n")

        new_content = "\n".join(format_lines(lines, mode))

        if new_content == content:
            result = "unchanged"
        else:
            err.print(f"would reformat {path}", style="bold", highlight=False)

            if diff:
                diff_ = unified_diff(content, new_content, path)

                if color:
                    formatted_diff = diff_highlighter(diff_)
                else:
                    formatted_diff = Text(diff_)

                out.print(formatted_diff)

            result = "reformatted"
    except (black.InvalidInput, formats.InvalidFormatError) as e:
        err.print(
            f"error: cannot format {path.absolute()}: {e}", style="red", highlight=False
        )
        result = "error"

    return result


def process(args):
    if not args.src:
        err.print("No Path provided. Nothing to do :sleeping:", style="bold")
        return 0

    selected_formats = getattr(args, "formats", None)
    if selected_formats:
        formats.disable(
            set(formats.detection_funcs.keys()) - set(selected_formats) - {"none"}
        )

    disabled_formats = getattr(args, "disable_formats", None)
    if disabled_formats:
        formats.disable(disabled_formats)

    try:
        include_regex = black.re_compile_maybe_verbose(args.include)
    except black.re.error:
        err.print(
            f"Invalid regular expression for include given: {args.include!r}",
            style="red",
        )
        return 2

    try:
        exclude_regex = black.re_compile_maybe_verbose(args.exclude)
    except black.re.error:
        err.print(
            f"Invalid regular expression for exclude given: {args.exclude!r}",
            style="red",
        )
        return 2

    try:
        extend_exclude_regex = black.re_compile_maybe_verbose(args.extend_exclude)
    except black.re.error:
        err.print(
            f"Invalid regular expression for extend exclude given: {args.extend_exclude!r}",
            style="red",
        )
        return 2

    try:
        force_exclude = getattr(args, "force_exclude", "")
        force_exclude_regex = (
            black.re_compile_maybe_verbose(force_exclude) if force_exclude else None
        )
    except black.re.error:
        err.print(
            f"Invalid regular expression for force_exclude given: {force_exclude!r}",
            style="red",
        )
        return 2

    sources = set(
        collect_files(
            args.src,
            include_regex,
            exclude_regex,
            extend_exclude_regex,
            force_exclude_regex,
            quiet=args.quiet,
            verbose=args.verbose,
        )
    )
    if len(sources) == 0:
        err.print(
            "No files are present to be formatted. Nothing to do :sleeping:",
            style="bold",
        )
        return 0

    target_versions = set(
        black.TargetVersion[version.upper()]
        for version in getattr(args, "target_versions", ())
    )
    mode = black.Mode(
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
        source: action(source.resolve(), mode, **action_kwargs)
        for source in sorted(sources)
    }

    conditional = args.action == "check"
    report = Report.from_sources(changed_sources, conditional=conditional)

    if report.n_error > 0:
        return_code = 123
    elif args.action == "check" and report.n_reformatted > 0:
        return_code = 1
    else:
        return_code = 0

    error_message = "Oh no! :boom: :broken_heart: :boom:"
    no_error_message = "All done! :sparkles: :cake: :sparkles:"
    err.print()
    err.print(
        error_message if report.n_error > 0 else no_error_message,
        style="bold",
    )
    err.print(report, highlight=False)
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
            "Python versions that should be supported by Black's output."
            " (default: per-file auto-detection)"
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
            "Don't write the files back, just return the status.  Return code 0"
            " means nothing would change.  Return code 1 means some files would be"
            " reformatted.  Return code 123 means there was an internal error."
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
            "A regular expression that matches files and directories that should be"
            " included on recursive searches.  An empty value means all files are"
            " included regardless of the name.  Use forward slashes for directories on"
            " all platforms (Windows, too).  Exclusions are calculated first, inclusions"
            " later."
        ),
    )
    parser.add_argument(
        "--exclude",
        metavar="TEXT",
        type=str,
        default=black.DEFAULT_EXCLUDES,
        help=(
            "A regular expression that matches files and directories that should be"
            " excluded on recursive searches.  An empty value means no paths are excluded."
            " Use forward slashes for directories on all platforms (Windows, too)."
            "  Exclusions are calculated first, inclusions later."
        ),
    )
    parser.add_argument(
        "--extend-exclude",
        metavar="TEXT",
        type=str,
        default="",
        help=(
            "Like --exclude, but adds additional files and directories"
            " on top of the excluded ones. (Useful if you simply want to"
            " add to the default)"
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
            "Disable the given formats."
            " This option also affects formats explicitly set."
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
        "-q",
        "--quiet",
        action="store_true",
        help=(
            "Don't emit non-error messages to stderr. Errors are still"
            " emitted; silence those with 2>/dev/null."
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help=(
            "Also emit messages to stderr about files that were not"
            " changed or were ignored due to exclusion patterns."
        ),
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
