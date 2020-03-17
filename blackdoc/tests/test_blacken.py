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
    ),
)
def test_parse_message(message, expected):
    actual = parse_message(message)
    assert expected == actual
