import textwrap

import more_itertools
import pytest

from blackdoc import blacken
from blackdoc.formats import doctest
from blackdoc.tests.data import doctest as data


@pytest.mark.parametrize(
    ("string", "expected"),
    (
        pytest.param("", None, id="empty string"),
        pytest.param("a", None, id="no quotes"),
        pytest.param("'''a'''", "'''", id="single quotes"),
        pytest.param('"""a"""', '"""', id="double quotes"),
        pytest.param('"a"""', None, id="trailing empty string"),
        pytest.param(
            textwrap.dedent(
                """\
                '''
                multiple lines
                '''
                """
            ).rstrip(),
            "'''",
            id="multiple lines single quotes",
        ),
        pytest.param(
            textwrap.dedent(
                '''\
                """
                multiple lines
                """
                '''
            ).rstrip(),
            '"""',
            id="multiple lines double quotes",
        ),
    ),
)
def test_detect_docstring_quotes(string, expected):
    actual = doctest.detect_docstring_quotes(string)
    assert expected == actual


@pytest.mark.parametrize(
    ["string", "expected"],
    (
        pytest.param("", None, id="empty_line"),
        pytest.param("a function to open lines", None, id="no_code"),
        pytest.param(">>>", "doctest", id="empty_line_with_prompt"),
        pytest.param(">>> 10 * 5", "doctest", id="single_line"),
        pytest.param("    >>> 10 * 5", "doctest", id="single_line_with_indent"),
        pytest.param(
            textwrap.dedent(
                """\
                >>> a = [
                ...     1,
                ...     2,
                ... ]
                """
            ),
            "doctest",
            id="multiple_lines",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                >>> ''' arbitrary triple-quoted string
                ...
                ... with empty continuation line
                ... '''
                """
            ),
            "doctest",
            id="multiple_lines_with_empty_continuation_line",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                >>>
                ... '''arbitrary triple-quoted string'''
                """
            ),
            "doctest",
            id="multiple_lines_with_leading_empty_continuation_line",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                >>> '''arbitrary triple-quoted string'''
                ...
                """
            ),
            "doctest",
            id="multiple_lines_with_trailing_empty_continuation_line",
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
    lines_ = more_itertools.peekable(enumerate(lines, start=1))

    actual = doctest.detection_func(lines_)
    assert actual == construct_expected(expected, string.rstrip())


@pytest.mark.parametrize(
    ["code_unit", "expected"],
    (
        pytest.param(
            ">>>", ({"prompt_length": 4, "docstring_quotes": None}, ""), id="empty_line"
        ),
        pytest.param(
            ">>> 10 * 5",
            ({"prompt_length": 4, "docstring_quotes": None}, "10 * 5"),
            id="single_line",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                >>> a = [
                ...     1,
                ...     2,
                ...     3,
                ... ]
                """.rstrip()
            ),
            (
                {"prompt_length": 4, "docstring_quotes": None},
                textwrap.dedent(
                    """\
                    a = [
                        1,
                        2,
                        3,
                    ]
                    """.rstrip()
                ),
            ),
            id="multiple_lines",
        ),
        pytest.param(
            ">>> s = '''abc'''",
            (
                {"prompt_length": 4, "docstring_quotes": "'''"},
                "s = '''abc'''",
            ),
            id="triple_quoted_string-single_quotes",
        ),
        pytest.param(
            '>>> s = """abc"""',
            (
                {"prompt_length": 4, "docstring_quotes": '"""'},
                's = """abc"""',
            ),
            id="triple_quoted_string-double_quotes",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                >>> ''' arbitrary triple-quoted string
                ...
                ... with empty continuation line
                ... '''
                """.rstrip()
            ),
            (
                {"prompt_length": 4, "docstring_quotes": "'''"},
                textwrap.dedent(
                    """\
                    ''' arbitrary triple-quoted string

                    with empty continuation line
                    '''
                    """.rstrip()
                ),
            ),
            id="multiple_lines_with_empty_continuation_line",
        ),
    ),
)
def test_extraction_func(code_unit, expected):
    actual = doctest.extraction_func(code_unit)

    assert expected == actual


def prepare_lines(lines, remove_prompt=False):
    dedented = (line.lstrip() for line in more_itertools.always_iterable(lines))
    prepared = dedented if not remove_prompt else (line[4:] for line in dedented)
    return "\n".join(prepared)


@pytest.mark.parametrize(
    ["code_unit", "docstring_quotes", "expected"],
    (
        pytest.param(
            "file",
            None,
            ">>> file",
            id="single line",
        ),
        pytest.param(
            "",
            None,
            ">>>",
            id="single empty line",
        ),
        pytest.param(
            '"""docstring"""',
            '"""',
            '>>> """docstring"""',
            id="single-line triple-quoted string",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                a = [
                    1,
                    2,
                ]
                """.rstrip()
            ),
            None,
            textwrap.dedent(
                """\
                >>> a = [
                ...     1,
                ...     2,
                ... ]
                """.rstrip()
            ),
            id="multiple lines",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                print("abc")
                print("def")
                """
            ),
            None,
            textwrap.dedent(
                """\
                >>> print("abc")
                >>> print("def")
                """.rstrip()
            ),
            id="multiple lines multiple statements",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                # comment
                print("abc")
                """
            ),
            None,
            textwrap.dedent(
                """\
                >>> # comment
                ... print("abc")
                """.rstrip()
            ),
            id="multiple lines with comment",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                # comment
                def func():
                    pass
                """
            ),
            None,
            textwrap.dedent(
                """\
                >>> # comment
                ... def func():
                ...     pass
                ...
                """.rstrip()
            ),
            id="multiple lines comment before block",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                @decorator
                def func():
                    pass
                """
            ),
            None,
            textwrap.dedent(
                """\
                >>> @decorator
                ... def func():
                ...     pass
                ...
                """.rstrip()
            ),
            id="multiple lines function decorator",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                @decorator
                class A:
                    pass
                """
            ),
            None,
            textwrap.dedent(
                """\
                >>> @decorator
                ... class A:
                ...     pass
                ...
                """.rstrip()
            ),
            id="multiple lines class decorator",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                '''
                docstring content
                '''
                """.rstrip()
            ),
            "'''",
            textwrap.dedent(
                """\
                >>> '''
                ... docstring content
                ... '''
                """.rstrip()
            ),
            id="multi-line triple-quoted string-single quotes",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                s = '''
                    triple-quoted string
                '''
                """
            ).rstrip(),
            '"""',
            textwrap.dedent(
                '''\
                >>> s = """
                ...     triple-quoted string
                ... """
                '''.rstrip(),
            ),
            id="multi-line triple-quoted string-double quotes",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                ''' arbitrary triple-quoted string

                with a empty continuation line
                '''
                """.rstrip(),
            ),
            "'''",
            textwrap.dedent(
                """\
                >>> ''' arbitrary triple-quoted string
                ...
                ... with a empty continuation line
                ... '''
                """.rstrip(),
            ),
            id="multi-line triple-quoted string with empty continuation line",
        ),
        pytest.param(
            '"""inverted quotes"""',
            '"""',
            '>>> """inverted quotes"""',
            id="triple-quoted string with inverted quotes",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                def myfunc(arg1, arg2):
                    pass
                """
            ),
            None,
            textwrap.dedent(
                """\
                >>> def myfunc(arg1, arg2):
                ...     pass
                ...
                """.rstrip()
            ),
            id="trailing newline at the end of a block",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                a = 1

                """
            ),
            None,
            ">>> a = 1",
            id="trailing newline at the end of a normal line",
        ),
        pytest.param(
            "# this is not a block:",
            None,
            ">>> # this is not a block:",
            id="trailing colon at the end of a comment",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                def f(arg1, arg2):
                    ''' nested docstring

                    parameter description
                    '''
                """
            ),
            "'''",
            textwrap.dedent(
                """\
                >>> def f(arg1, arg2):
                ...     ''' nested docstring
                ...
                ...     parameter description
                ...     '''
                ...
                """.rstrip()
            ),
            id="nested docstring",
        ),
        pytest.param(
            "s = '''triple-quoted string'''",
            '"""',
            '>>> s = """triple-quoted string"""',
            id="triple-quoted string",
        ),
        pytest.param(
            textwrap.dedent(
                '''\
                def f(arg1, arg2):
                    """ docstring """
                    s = "trailing empty string"""
                '''
            ),
            "'''",
            textwrap.dedent(
                """\
                >>> def f(arg1, arg2):
                ...     ''' docstring '''
                ...     s = "trailing empty string\"""
                ...
                """.rstrip()
            ),
            id="docstring and trailing empty string",
        ),
        pytest.param(
            textwrap.dedent(
                '''\
                def f(arg1, arg2):
                    """ docstring """
                    s = """triple-quoted string"""
                '''
            ),
            "'''",
            textwrap.dedent(
                """\
                >>> def f(arg1, arg2):
                ...     ''' docstring '''
                ...     s = '''triple-quoted string'''
                ...
                """.rstrip()
            ),
            id="docstring and triple-quoted string",
        ),
    ),
)
def test_reformatting_func(code_unit, docstring_quotes, expected):
    actual = doctest.reformatting_func(code_unit, docstring_quotes)
    assert expected == actual

    # make sure the docstring quotes were not changed
    expected_quotes = doctest.detect_docstring_quotes(expected)
    actual_quotes = doctest.detect_docstring_quotes(actual)
    assert expected_quotes == actual_quotes


def test_blacken():
    labeled = tuple(
        ((min_ + 1, max_ + 1), label, "\n".join(data.lines[slice(min_, max_)]))
        for label, (min_, max_) in zip(data.line_labels, data.line_ranges)
    )
    actual = tuple(blacken(labeled))

    assert len("\n".join(actual).split("\n")) == 32
