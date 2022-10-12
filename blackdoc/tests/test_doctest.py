import textwrap

import more_itertools
import pytest

from blackdoc.formats import doctest

from .data.doctest import lines


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
    "line",
    (
        pytest.param(textwrap.dedent(lines[8]), id="single line"),
        pytest.param(textwrap.dedent(lines[23]), id="single empty line"),
        pytest.param(textwrap.dedent("\n".join(lines[4:8])), id="multiple lines"),
        pytest.param(
            textwrap.dedent("\n".join(lines[17:23])),
            id="multiple lines with empty continuation line",
        ),
    ),
)
def test_extraction_func(line):
    docstring_quotes = doctest.detect_docstring_quotes(line)

    expected = (
        {"prompt_length": doctest.prompt_length, "docstring_quotes": docstring_quotes},
        "\n".join(line.lstrip()[4:] for line in line.split("\n")),
    )
    actual = doctest.extraction_func(line)

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
            id="multi-line triple-quoted string",
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
            id="multi-line triple-quoted string",
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
