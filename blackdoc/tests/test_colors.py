import re

from blackdoc import colors


def test_color_diff_trailing_whitespace():
    # can't use triple-quotes because the formatters would remove the trailing whitespace
    line = ">>> a"
    whitespace = " " * 5
    contents = "\n".join(
        [
            f"-{line}{whitespace}",
            f"+{line}",
        ]
    )
    colorized = colors.color_diff(contents)

    pattern = colors.colors_re.pattern
    expected_pattern = re.compile(rf"{pattern}\s+{pattern}")
    match = expected_pattern.search(colorized)

    assert match is not None and whitespace in match.group(0)
