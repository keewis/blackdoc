def report_changes(n_reformatted, n_unchanged, n_error):
    def noun(n):
        return "file" if n < 2 else "files"

    reports = []
    if n_reformatted > 0:
        reports.append(
            f"[bold white]{n_reformatted} {noun(n_reformatted)} reformatted[/]",
        )

    if n_unchanged > 0:
        reports.append(f"[white]{n_unchanged} {noun(n_unchanged)} left unchanged[/]")

    if n_error > 0:
        reports.append(f"[red]{n_error} {noun(n_error)} fails to reformat[/]")

    return ", ".join(reports) + "."


def report_possible_changes(n_reformatted, n_unchanged, n_error):
    def noun(n):
        return "file" if n < 2 else "files"

    reports = []
    if n_reformatted > 0:
        reports.append(
            f"[bold white]{n_reformatted} {noun(n_reformatted)} would be reformatted[/]",
        )

    if n_unchanged > 0:
        reports.append(
            f"[white]{n_unchanged} {noun(n_unchanged)} would be left unchanged[/]"
        )

    if n_error > 0:
        reports.append(f"[red]{n_error} {noun(n_error)} would fail to reformat[/]")

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
