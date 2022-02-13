from .colors import colorize


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
