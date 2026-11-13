import textwrap

import pytest

from blackdoc.blacken import parse_message


@pytest.mark.parametrize(
    "message,expected",
    (
        pytest.param(
            'Cannot parse: 16:10: with new_open("abc) as f:',
            ("Cannot parse", 16, 10, 'with new_open("abc) as f:'),
            id="simple_message",
        ),
        pytest.param(
            textwrap.dedent(
                '''\
                Cannot parse: 1:26
                    {calculation}(skipna=False)""",
                                             ^
                TokenError: Unexpected EOF in multi-line statement
                '''.rstrip(),
            ),
            (
                "Cannot parse",
                1,
                26,
                "\n".join(
                    [
                        '    {calculation}(skipna=False)""",',
                        "                             ^",
                        "TokenError: Unexpected EOF in multi-line statement",
                    ]
                ),
            ),
            id="multiline",
        ),
    ),
)
def test_parse_message(message, expected):
    actual = parse_message(message)
    assert expected == actual
