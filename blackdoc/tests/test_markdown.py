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


@pytest.mark.parametrize(
    ["code", "expected"],
    (
        pytest.param(
            textwrap.dedent(
                """\
                ```python
                10 * 5
                ```
                """.rstrip()
            ),
            (
                {
                    "language": "python",
                    "fences": "```",
                    "prompt_length": 0,
                },
                "10 * 5",
            ),
            id="backticks",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ``` python
                10 * 5
                ```
                """.rstrip()
            ),
            (
                {
                    "language": "python",
                    "prompt_length": 0,
                    "fences": "```",
                },
                "10 * 5",
            ),
            id="backticks-with_space",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```{python}
                10 * 5
                ```
                """.rstrip()
            ),
            (
                {
                    "language": "python",
                    "prompt_length": 0,
                    "fences": "```",
                },
                "10 * 5",
            ),
            id="backticks-with_braces",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                :::python
                10 * 5
                :::
                """.rstrip()
            ),
            (
                {
                    "language": "python",
                    "prompt_length": 0,
                    "fences": ":::",
                },
                "10 * 5",
            ),
            id="colons",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ::: python
                10 * 5
                :::
                """.rstrip()
            ),
            (
                {
                    "language": "python",
                    "prompt_length": 0,
                    "fences": ":::",
                },
                "10 * 5",
            ),
            id="colons-with_space",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                :::{python}
                10 * 5
                :::
                """.rstrip()
            ),
            (
                {
                    "language": "python",
                    "prompt_length": 0,
                    "fences": ":::",
                },
                "10 * 5",
            ),
            id="colons-with_braces",
        ),
    ),
)
def test_extraction_func(code, expected):
    actual = markdown.extraction_func(code)

    assert expected == actual


@pytest.mark.parametrize(
    ("code", "directive", "expected"),
    (
        pytest.param(
            "10 * 5",
            {
                "language": "python",
                "fences": "```",
            },
            textwrap.dedent(
                """\
                ```python
                10 * 5
                ```
                """.rstrip()
            ),
            id="backticks",
        ),
        pytest.param(
            "10 * 5",
            {
                "language": "python",
                "fences": ":::",
            },
            textwrap.dedent(
                """\
                :::python
                10 * 5
                :::
                """.rstrip()
            ),
            id="colons",
        ),
    ),
)
def test_reformatting_func(code, directive, expected):
    actual = markdown.reformatting_func(code, **directive)

    assert expected == actual
