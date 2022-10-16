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
            [Span(0, 15, "bold"), Span(16, 31, "bold")],
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


@pytest.mark.parametrize(
    ["text", "spans"],
    (
        pytest.param(
            "1 file would be reformatted",
            [Span(0, 6, "blue")],
            id="single file conditional",
        ),
        pytest.param(
            "1 file reformatted",
            [Span(0, 6, "blue")],
            id="single file",
        ),
        pytest.param(
            "26 files would be reformatted",
            [Span(0, 8, "blue")],
            id="multiple files conditional",
        ),
        pytest.param(
            "26 files reformatted",
            [Span(0, 8, "blue")],
            id="multiple files",
        ),
        pytest.param(
            "1 file would fail to reformat",
            [Span(0, 29, "red")],
            id="failed single file conditional",
        ),
        pytest.param(
            "1 file failed to reformat",
            [Span(0, 25, "red")],
            id="failed single file",
        ),
        pytest.param(
            "15 files would fail to reformat",
            [Span(0, 31, "red")],
            id="failed multiple files conditional",
        ),
        pytest.param(
            "15 files failed to reformat",
            [Span(0, 27, "red")],
            id="failed multiple files",
        ),
    ),
)
def test_file_highlighter(text, spans):
    highlighter = colors.FileHighlighter()

    actual = highlighter(text)
    assert actual.spans == spans
