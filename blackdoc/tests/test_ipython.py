import textwrap

import more_itertools
import pytest

from blackdoc import blacken
from blackdoc.formats import ipython

from .data import ipython as data


@pytest.mark.parametrize(
    ["lines", "expected"],
    (
        pytest.param("xyz def", None, id="no_line"),
        pytest.param(
            "    In [2]: file",
            ((1, 2), ipython.name, "    In [2]: file"),
            id="single_line",
        ),
        pytest.param(
            [
                "In [1]: file = open(",
                '   ...:     "very_long_filepath",',
                '   ...:     mode="a",',
                "   ...: )",
            ],
            (
                (1, 5),
                ipython.name,
                textwrap.dedent(
                    """\
            In [1]: file = open(
               ...:     "very_long_filepath",
               ...:     mode="a",
               ...: )
            """.rstrip()
                ),
            ),
            id="multiple_lines",
        ),
    ),
)
def test_detection_func(lines, expected):
    lines = more_itertools.peekable(
        enumerate(more_itertools.always_iterable(lines), start=1)
    )

    actual = ipython.detection_func(lines)
    assert actual == expected


@pytest.mark.parametrize(
    ["line", "expected"],
    (
        pytest.param(
            "In [2]: file",
            ({"count": 2}, "file"),
            id="single_line",
        ),
        pytest.param(
            textwrap.dedent(
                """\
            In [1]: file = open(
               ...:     "very_long_filepath",
               ...:     mode="a",
               ...: )
            """.rstrip()
            ),
            (
                {"count": 1},
                "\n".join(
                    [
                        "file = open(",
                        '    "very_long_filepath",',
                        '    mode="a",',
                        ")",
                    ]
                ),
            ),
            id="multiple_lines",
        ),
        pytest.param(
            textwrap.dedent(
                """\
            In [4]: %%time
               ...: file.close()
            """.rstrip()
            ),
            (
                {"count": 4},
                textwrap.dedent(
                    f"""\
                # {ipython.magic_comment}%%time
                file.close()
                """.rstrip()
                ),
            ),
            id="lines_with_cell_magic",
        ),
        pytest.param(
            textwrap.dedent(
                """\
                In [5]: @savefig simple.png width=4in
                   ...: @property
                   ...: def my_property(self):
                   ...:     pass
                """.rstrip()
            ),
            (
                {"count": 5},
                textwrap.dedent(
                    f"""\
                    # {ipython.magic_comment}@savefig simple.png width=4in
                    @property
                    def my_property(self):
                        pass
                    """.rstrip()
                ),
            ),
            id="lines_with_line_decorator",
        ),
    ),
)
def test_extraction_func(line, expected):
    actual = ipython.extraction_func(line)

    assert expected == actual


@pytest.mark.parametrize(
    "line,count,expected",
    (
        pytest.param(
            textwrap.dedent(data.lines[9])[8:],
            2,
            textwrap.dedent(data.lines[9]),
            id="single_line",
        ),
        pytest.param(
            "\n".join(line[12:] for line in data.lines[4:8]),
            1,
            textwrap.dedent("\n".join(data.lines[4:8])),
            id="multiple_lines",
        ),
        pytest.param(
            "\n".join(
                line[12:]
                if not ipython.magic_re.match(line)
                else f"#{ipython.magic_comment}{line[12:]}"
                for line in data.lines[18:20]
            ),
            4,
            textwrap.dedent("\n".join(data.lines[18:20])),
            id="lines_with_cell_magic",
        ),
        pytest.param(
            "\n".join(
                line[12:]
                if not ipython.magic_re.match(line)
                else f"#{ipython.magic_comment}{line[12:]}"
                for line in data.lines[21:25]
            ),
            5,
            textwrap.dedent("\n".join(data.lines[21:25])),
            id="lines_with_line_decorator",
        ),
    ),
)
def test_reformatting_func(line, count, expected):
    actual = ipython.reformatting_func(line, count=count)
    assert expected == actual


def test_blacken():
    labeled = list(
        (
            (min_, max_),
            label,
            "\n".join(data.lines[min_:max_]),
        )
        for (min_, max_), label in zip(data.line_ranges, data.line_labels)
    )
    actual = tuple(blacken(labeled))

    assert len(actual) == 19
