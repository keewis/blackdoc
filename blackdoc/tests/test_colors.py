import textwrap

import pytest
from rich.text import Span

from blackdoc import colors


@pytest.mark.parametrize(
    ["text", "spans"],
    (
        pytest.param(
            textwrap.dedent(
                """\
                - >>> a
                + >>> a + 1
                """.rstrip()
            ),
            [Span(0, 7, "red"), Span(8, 19, "green")],
            id="simple replacement",
        ),
        pytest.param(
            textwrap.dedent(
                f"""\
                - >>> a{' ' * 5}
                + >>> a + 1
                """.rstrip()
            ),
            [Span(0, 7, "red"), Span(7, 12, "red on red"), Span(13, 24, "green")],
            id="trailing whitespace",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                --- file1 time1
                +++ file2 time2
                """
            ),
            [Span(0, 15, "bold white"), Span(16, 31, "bold white")],
            id="header",
        ),
        pytest.param(
            "@@ line1,line2",
            [Span(0, 14, "cyan")],
            id="block header",
        ),
    ),
)
def test_diff_highlighter(text, spans):
    diff_highlighter = colors.DiffHighlighter()

    actual = diff_highlighter(text)
    assert actual.spans == spans
