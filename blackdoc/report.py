from rich.text import Text

from .colors import FileHighlighter

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

    @property
    def _reformatted_report(self):
        if self.conditional:
            return (
                f"{self.n_reformatted} {noun(self.n_reformatted)} would be reformatted"
            )
        else:
            return f"{self.n_reformatted} {noun(self.n_reformatted)} reformatted"

    @property
    def _unchanged_report(self):
        if self.conditional:
            return (
                f"{self.n_unchanged} {noun(self.n_unchanged)} would be left unchanged"
            )
        else:
            return f"{self.n_unchanged} {noun(self.n_unchanged)} left unchanged"

    @property
    def _error_report(self):
        if self.conditional:
            return f"{self.n_error} {noun(self.n_error)} would fail to reformat"
        else:
            return f"{self.n_error} {noun(self.n_error)} failed to reformat"

    def __rich__(self):
        raw_parts = [
            self._reformatted_report,
            self._unchanged_report,
            self._error_report,
        ]
        parts = [highlighter(part) for part in raw_parts]
        return Text(", ").join(parts) + Text(".")
