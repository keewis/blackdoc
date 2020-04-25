import more_itertools
import pytest

from ..formats import rst
from .data import rst as data


@pytest.mark.parametrize(
    "lines,expected",
    (
        pytest.param(data.lines[0], None, id="none"),
        pytest.param(
            data.lines[2:11], ((3, 12), rst.code_block, data.lines[2:11]), id="code",
        ),
        pytest.param(
            data.lines[11:20],
            ((12, 21), rst.code_block, data.lines[11:20]),
            id="code-block",
        ),
        pytest.param(
            data.lines[21:30], ((22, 31), rst.ipython, data.lines[21:30]), id="ipython",
        ),
        pytest.param(
            data.lines[31:44],
            ((32, 45), rst.ipython_prompt, data.lines[31:44]),
            id="ipython-prompt",
        ),
    ),
)
def test_detection_func(lines, expected):
    lines = more_itertools.peekable(
        enumerate(more_itertools.always_iterable(lines), start=1)
    )

    actual = rst.detection_func(lines)
    assert actual == expected
