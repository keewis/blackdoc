from rich.text import Text

from blackdoc.colors import FileHighlighter

highlighter = FileHighlighter()


def statistics(sources):
    from collections import Counter

    statistics = Counter(sources.values())

    n_unchanged = statistics.pop("unchanged", 0)
    n_reformatted = statistics.pop("reformatted", 0)
    n_error = statistics.pop("error", 0)

    if len(statistics) != 0:
        raise RuntimeError(f"unknown results: {statistics.keys()}")

    return n_reformatted, n_unchanged, n_error


def noun(n):
    return "file" if n < 2 else "files"


def _report_words(report_type, conditional):
    mapping = {
        "reformatted": {
            False: "reformatted",
            True: "would be reformatted",
        },
        "unchanged": {
            False: "left unchanged",
            True: "would be left unchanged",
        },
        "error": {
            False: "failed to reformat",
            True: "would fail to reformat",
        },
    }

    return mapping.get(report_type, {}).get(conditional)


class Report:
    def __init__(self, n_reformatted, n_unchanged, n_error, conditional=False):
        self.n_reformatted = n_reformatted
        self.n_unchanged = n_unchanged
        self.n_error = n_error

        self.conditional = conditional

    @classmethod
    def from_sources(cls, sources, conditional=False):
        n_reformatted, n_unchanged, n_error = statistics(sources)

        return cls(n_reformatted, n_unchanged, n_error, conditional=conditional)

    def __repr__(self):
        params = [
            f"{name}={getattr(self, name)}"
            for name in ["n_reformatted", "n_unchanged", "n_error", "conditional"]
        ]
        return f"Report({', '.join(params)})"

    def _report_parts(self):
        report_types = ["reformatted", "unchanged", "error"]
        values = {
            report_type: getattr(self, f"n_{report_type}")
            for report_type in report_types
        }
        parts = [
            f"{value} {noun(value)} {_report_words(report_type, self.conditional)}"
            for report_type, value in values.items()
            if value > 0
        ]
        return parts

    def __str__(self):
        parts = self._report_parts()
        return ", ".join(parts) + "."

    def __rich__(self):
        parts = [highlighter(part) for part in self._report_parts()]
        return Text(", ").join(parts) + Text(".")
