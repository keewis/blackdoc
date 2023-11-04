import textwrap

import more_itertools
import pytest

from blackdoc import blacken
from blackdoc.formats import rst
from blackdoc.tests.data import rst as data


@pytest.mark.parametrize(
    ("string", "expected"),
    (
        pytest.param("", None, id="empty string"),
        pytest.param("Some string.", None, id="no_code"),
        pytest.param(
            textwrap.dedent(
                """\
                .. note::

                    This is not a code block.
                """
            ),
            None,
            id="block",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                .. code:: sh

                    find . -name "*.py"
                """
            ),
            None,
            id="code_other_language",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                .. code:: python

                    10 * 5
                """
            ),
            "rst",
            id="code",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                .. code-block:: python

                    10 * 5
                """
            ),
            "rst",
            id="code-block",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                .. ipython:: python

                    %%time
                    10 * 5
                """
            ),
            "rst",
            id="ipython",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                .. ipython::

                    In [1]: 10 * 5
                    Out[1]: 50

                    In [2]: %%time
                       ...: ".".join("abc")
                    Out[2]: 'a.b.c'
                """
            ),
            None,
            id="ipython-prompt",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                .. ipython::
                    :okerror:

                    @verbatim
                    In [1]: 10 * 5
                    Out[1]: 50
                """
            ),
            None,
            id="ipython-prompt-cell-decorator",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                .. testsetup::

                    10 * 5
                """
            ),
            "rst",
            id="testsetup",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                .. testcode::

                    10 * 5
                """
            ),
            "rst",
            id="testcode",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                .. testcleanup::

                    10 * 5
                """
            ),
            "rst",
            id="testcleanup",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                .. ipython:: python
                    print("abc")
                """
            ),
            "rst",
            id="missing option separator",
        ),
    ),
)
def test_detection_func(string, expected):
    def construct_expected(label, string):
        if label is None:
            return None

        n_lines = len(string.split("\n"))

        range_ = (1, n_lines + 1)
        return range_, label, string

    lines = string.split("\n")
    code_fragment = more_itertools.peekable(enumerate(lines, start=1))
    actual = rst.detection_func(code_fragment)

    assert actual == construct_expected(expected, string.rstrip())


@pytest.mark.parametrize(
    "code,expected",
    (
        pytest.param(
            textwrap.dedent(
                """\
                .. code:: python

                   10 * 5
                """.rstrip()
            ),
            (
                {
                    "name": "code",
                    "language": "python",
                    "options": (),
                    "prompt_length": 3,
                    "n_header_lines": 2,
                },
                "10 * 5",
            ),
            id="code",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                .. code:: python
                   :okwarning:

                   10 * 5
                """.rstrip()
            ),
            (
                {
                    "name": "code",
                    "language": "python",
                    "options": (":okwarning:",),
                    "prompt_length": 3,
                    "n_header_lines": 3,
                },
                "10 * 5",
            ),
            id="code_with_options",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                .. code-block:: python

                   10 * 5
                """.rstrip()
            ),
            (
                {
                    "name": "code-block",
                    "language": "python",
                    "options": (),
                    "prompt_length": 3,
                    "n_header_lines": 2,
                },
                "10 * 5",
            ),
            id="code-block",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                .. ipython::

                    %%time
                    10 * 5
                """.rstrip()
            ),
            (
                {
                    "name": "ipython",
                    "language": None,
                    "options": (),
                    "prompt_length": 4,
                    "n_header_lines": 2,
                },
                textwrap.dedent(
                    """\
                    # <ipython-magic>%%time
                    10 * 5
                    """.rstrip()
                ),
            ),
            id="ipython",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                .. ipython:: python
                    10 * 5
                """.rstrip()
            ),
            (
                {
                    "name": "ipython",
                    "language": "python",
                    "options": (),
                    "prompt_length": 4,
                    "n_header_lines": 2,
                },
                "10 * 5",
            ),
            id="missing_eof_line",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                .. ipython:: python
                    print("abc")
                """.rstrip()
            ),
            (
                {
                    "name": "ipython",
                    "language": "python",
                    "options": (),
                    "prompt_length": 4,
                    "n_header_lines": 2,
                },
                'print("abc")',
            ),
            id="missing_sep_line",
        ),
    ),
)
def test_extraction_func(code, expected):
    actual = rst.extraction_func(code)

    assert expected == actual


@pytest.mark.parametrize(
    ("code", "directive", "expected"),
    (
        pytest.param(
            "10 * 5",
            {
                "name": "code",
                "language": "python",
                "options": (),
                "prompt_length": 3,
            },
            textwrap.dedent(
                """\
                .. code:: python

                   10 * 5
                """.rstrip()
            ),
            id="code",
        ),
        pytest.param(
            "10 * 5",
            {
                "name": "code-block",
                "language": "python",
                "options": (":okwarning:",),
                "prompt_length": 4,
            },
            textwrap.dedent(
                """\
                .. code-block:: python
                    :okwarning:

                    10 * 5
                """.rstrip()
            ),
            id="code-block_with_options",
        ),
        pytest.param(
            "10 * 5",
            {"name": "ipython", "language": None, "options": (), "prompt_length": 4},
            textwrap.dedent(
                """\
                .. ipython::

                    10 * 5
                """.rstrip()
            ),
            id="ipython",
        ),
    ),
)
def test_reformatting_func(code, directive, expected):
    actual = rst.reformatting_func(code, **directive)

    assert expected == actual


def test_blacken():
    labeled = tuple(
        ((min_ + 1, max_ + 1), label, "\n".join(data.lines[slice(min_, max_)]))
        for label, (min_, max_) in zip(data.line_labels, data.line_ranges)
    )
    actual = tuple(blacken(labeled))

    assert len("\n".join(actual).split("\n")) == 76
