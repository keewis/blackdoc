import textwrap

import more_itertools
import pytest

from blackdoc.formats import markdown


@pytest.mark.parametrize(
    ["string", "expected"],
    (
        pytest.param("", None, id="empty string"),
        pytest.param("Some string.", None, id="no_code"),
        pytest.param(
            textwrap.dedent(
                """\
                ```
                This is not a code block.
                ```
                """
            ),
            None,
            id="block",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```sh
                find . -name "*.py"
                ```
                """
            ),
            None,
            id="code_other_language",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```python
                10 * 5
                ```
                """
            ),
            "markdown",
            id="code",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ``` python
                10 * 5
                ```
                """
            ),
            "markdown",
            id="code-space",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```{python}
                10 * 5
                ```
                """
            ),
            "markdown",
            id="code-braces",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                :::python
                10 * 5
                :::
                """
            ),
            "markdown",
            id="myst-code",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                :::{python}
                10 * 5
                :::
                """
            ),
            "markdown",
            id="myst-code-braces",
        ),
    ),
)
def test_detection_func(string, expected):
    def construct_expected(label, string):
        if label is None:
            return None

        n_lines = len(string.split("\n"))

        range_ = (1, n_lines + 2)
        return range_, label, string

    lines = string.split("\n")
    code_fragment = more_itertools.peekable(enumerate(lines, start=1))
    actual = markdown.detection_func(code_fragment)

    assert actual == construct_expected(expected, string.rstrip())
