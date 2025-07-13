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
                >>> 10 * 5
                ```
                """
            ),
            None,
            id="doctest_prompt",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```python
                In [1]: 10 * 5
                Out[1]:
                50
                ```
                """
            ),
            None,
            id="ipython_prompt",
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
                ```jupyter-execute
                10 * 5
                ```
                """
            ),
            "markdown",
            id="jupyter-execute",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```{jupyter-execute}
                10 * 5
                ```
                """
            ),
            "markdown",
            id="jupyter-execute-braces",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```{jupyter-execute}
                ---
                hide-code: true
                ---
                10 * 5
                ```
                """
            ),
            "markdown",
            id="jupyter-execute-braces-with_options",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```{jupyter-execute}
                ---
                hide-code: true
                ---

                10 * 5
                ```
                """
            ),
            "markdown",
            id="jupyter-execute-braces-with_options-with_newlines",
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
        pytest.param(
            textwrap.dedent(
                """\
                :::{python}
                10 * 5
                :::
                """
            ),
            "markdown",
            id="myst-jupyter-execute",
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
            id="myst-jupyter-execute-braces",
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
                    "block_type": "python",
                    "prompt_length": 0,
                    "fences": "```",
                    "braces": False,
                    "language": None,
                    "options": (),
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
                    "block_type": "python",
                    "prompt_length": 0,
                    "fences": "```",
                    "braces": False,
                    "language": None,
                    "options": (),
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
                    "block_type": "python",
                    "prompt_length": 0,
                    "fences": "```",
                    "braces": True,
                    "language": None,
                    "options": (),
                },
                "10 * 5",
            ),
            id="backticks-with_braces",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```{jupyter-execute}
                10 * 5
                ```
                """.rstrip()
            ),
            (
                {
                    "block_type": "jupyter-execute",
                    "prompt_length": 0,
                    "fences": "```",
                    "braces": True,
                    "language": None,
                    "options": (),
                },
                "10 * 5",
            ),
            id="backticks-jupyter-execute-with_braces",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```{jupyter-execute}
                ---
                hide-code: true
                hide-output: true
                ---
                10 * 5
                ```
                """.rstrip()
            ),
            (
                {
                    "block_type": "jupyter-execute",
                    "prompt_length": 0,
                    "fences": "```",
                    "braces": True,
                    "language": None,
                    "options": ("hide-code: true", "hide-output: true"),
                },
                "10 * 5",
            ),
            id="backticks-jupyter-execute-with_options",
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
                    "block_type": "python",
                    "prompt_length": 0,
                    "fences": ":::",
                    "braces": False,
                    "language": None,
                    "options": (),
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
                    "block_type": "python",
                    "prompt_length": 0,
                    "fences": ":::",
                    "braces": False,
                    "language": None,
                    "options": (),
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
                    "block_type": "python",
                    "prompt_length": 0,
                    "fences": ":::",
                    "braces": True,
                    "language": None,
                    "options": (),
                },
                "10 * 5",
            ),
            id="colons-with_braces",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                :::{jupyter-execute}
                10 * 5
                :::
                """.rstrip()
            ),
            (
                {
                    "block_type": "jupyter-execute",
                    "prompt_length": 0,
                    "fences": ":::",
                    "braces": True,
                    "language": None,
                    "options": (),
                },
                "10 * 5",
            ),
            id="colons-jupyter-execute",
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
                    "block_type": "python",
                    "prompt_length": 0,
                    "fences": "```",
                    "braces": True,
                    "language": None,
                    "options": (),
                },
                "10 * 5",
            ),
            id="backticks-with_braces",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```{jupyter-execute}
                10 * 5
                ```
                """.rstrip()
            ),
            (
                {
                    "block_type": "jupyter-execute",
                    "prompt_length": 0,
                    "fences": "```",
                    "braces": True,
                    "language": None,
                    "options": (),
                },
                "10 * 5",
            ),
            id="backticks-jupyter-execute-with_braces",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```{jupyter-execute}
                ---
                hide-code: true
                hide-output: true
                ---
                10 * 5
                ```
                """.rstrip()
            ),
            (
                {
                    "block_type": "jupyter-execute",
                    "prompt_length": 0,
                    "fences": "```",
                    "braces": True,
                    "language": None,
                    "options": ("hide-code: true", "hide-output: true"),
                },
                "10 * 5",
            ),
            id="backticks-jupyter-execute-with_options",
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
                    "block_type": "python",
                    "prompt_length": 0,
                    "fences": ":::",
                    "braces": False,
                    "language": None,
                    "options": (),
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
                    "block_type": "python",
                    "prompt_length": 0,
                    "fences": ":::",
                    "braces": False,
                    "language": None,
                    "options": (),
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
                    "block_type": "python",
                    "prompt_length": 0,
                    "fences": ":::",
                    "braces": True,
                    "language": None,
                    "options": (),
                },
                "10 * 5",
            ),
            id="colons-with_braces",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ```{code-cell} python
                10 * 5
                ```
                """.rstrip()
            ),
            (
                {
                    "block_type": "code-cell",
                    "prompt_length": 0,
                    "fences": "```",
                    "braces": True,
                    "language": "python",
                    "options": (),
                },
                "10 * 5",
            ),
            id="code-cell",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                :::python
                %load_ext extension
                10 * 5
                :::
                """.rstrip()
            ),
            (
                {
                    "block_type": "python",
                    "fences": ":::",
                    "braces": False,
                    "options": (),
                    "language": None,
                    "prompt_length": 0,
                },
                textwrap.dedent(
                    """\
                    # <ipython-magic>%load_ext extension
                    10 * 5
                    """.rstrip()
                ),
            ),
            id="ipython_magic",
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
                "block_type": "python",
                "fences": "```",
                "options": (),
                "language": None,
                "braces": False,
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
                "block_type": "jupyter-execute",
                "fences": "```",
                "braces": True,
                "language": None,
                "options": ("hide-code: true", "hide-output: true"),
            },
            textwrap.dedent(
                """\
                ```{jupyter-execute}
                ---
                hide-code: true
                hide-output: true
                ---
                10 * 5
                ```
                """.rstrip()
            ),
            id="jupyter-execute-with_options-with_braces",
        ),
        pytest.param(
            "10 * 5",
            {
                "block_type": "python",
                "fences": ":::",
                "braces": False,
                "language": None,
                "options": (),
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
        pytest.param(
            textwrap.dedent(
                """\
                # <ipython-magic>%load_ext extension
                10 * 5
                """.rstrip()
            ),
            {
                "block_type": "python",
                "fences": ":::",
                "braces": False,
                "language": None,
                "options": (),
            },
            textwrap.dedent(
                """\
                :::python
                %load_ext extension
                10 * 5
                :::
                """.rstrip()
            ),
            id="ipython_magic",
        ),
        pytest.param(
            "10 * 5",
            {
                "block_type": "code-cell",
                "fences": ":::",
                "braces": True,
                "language": "python",
                "options": (),
            },
            textwrap.dedent(
                """\
                :::{code-cell} python
                10 * 5
                :::
                """.rstrip()
            ),
            id="code-cell-colons",
        ),
    ),
)
def test_reformatting_func(code, directive, expected):
    actual = markdown.reformatting_func(code, **directive)

    assert expected == actual
