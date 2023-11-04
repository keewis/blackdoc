import pytest

from blackdoc import report


@pytest.mark.parametrize(
    ["sources", "expected"],
    (
        pytest.param(
            {
                "file1.py": "reformatted",
                "file2.py": "reformatted",
                "file3.rst": "reformatted",
            },
            (3, 0, 0),
            id="3 reformatted-0 unchanged-0 failed",
        ),
        pytest.param(
            {
                "file1.py": "unchanged",
                "file2.py": "unchanged",
                "file3.rst": "unchanged",
            },
            (0, 3, 0),
            id="0 reformatted-3 unchanged-0 failed",
        ),
        pytest.param(
            {"file1.py": "error", "file2.py": "error", "file3.rst": "error"},
            (0, 0, 3),
            id="0 reformatted-0 unchanged-3 failed",
        ),
        pytest.param(
            {"file1.py": "reformatted", "file2.py": "unchanged", "file3.rst": "error"},
            (1, 1, 1),
            id="1 reformatted-1 unchanged-1 failed",
        ),
    ),
)
def test_statistics(sources, expected):
    actual = report.statistics(sources)
    assert actual == expected


@pytest.mark.parametrize(
    ["statistics", "conditional", "expected"],
    (
        pytest.param(
            {"n_reformatted": 0, "n_unchanged": 1, "n_error": 0},
            False,
            ["1 file left unchanged"],
            id="0 reformatted-1 unchanged-0 failed",
        ),
        pytest.param(
            {"n_reformatted": 0, "n_unchanged": 1, "n_error": 0},
            True,
            ["1 file would be left unchanged"],
            id="0 reformatted-1 unchanged-0 failed-conditional",
        ),
        pytest.param(
            {"n_reformatted": 0, "n_unchanged": 4, "n_error": 0},
            False,
            ["4 files left unchanged"],
            id="0 reformatted-4 unchanged-0 failed",
        ),
        pytest.param(
            {"n_reformatted": 0, "n_unchanged": 4, "n_error": 0},
            True,
            ["4 files would be left unchanged"],
            id="0 reformatted-4 unchanged-0 failed-conditional",
        ),
        pytest.param(
            {"n_reformatted": 1, "n_unchanged": 0, "n_error": 0},
            False,
            ["1 file reformatted"],
            id="1 reformatted-0 unchanged-0 failed",
        ),
        pytest.param(
            {"n_reformatted": 1, "n_unchanged": 0, "n_error": 0},
            True,
            ["1 file would be reformatted"],
            id="1 reformatted-0 unchanged-0 failed-conditional",
        ),
        pytest.param(
            {"n_reformatted": 4, "n_unchanged": 0, "n_error": 0},
            False,
            ["4 files reformatted"],
            id="4 reformatted-0 unchanged-0 failed",
        ),
        pytest.param(
            {"n_reformatted": 4, "n_unchanged": 0, "n_error": 0},
            True,
            ["4 files would be reformatted"],
            id="4 reformatted-0 unchanged-0 failed-conditional",
        ),
        pytest.param(
            {"n_reformatted": 0, "n_unchanged": 0, "n_error": 1},
            False,
            ["1 file failed to reformat"],
            id="0 reformatted-0 unchanged-1 failed",
        ),
        pytest.param(
            {"n_reformatted": 0, "n_unchanged": 0, "n_error": 1},
            True,
            ["1 file would fail to reformat"],
            id="0 reformatted-0 unchanged-1 failed-conditional",
        ),
        pytest.param(
            {"n_reformatted": 0, "n_unchanged": 0, "n_error": 4},
            False,
            ["4 files failed to reformat"],
            id="0 reformatted-0 unchanged-4 failed",
        ),
        pytest.param(
            {"n_reformatted": 0, "n_unchanged": 0, "n_error": 4},
            True,
            ["4 files would fail to reformat"],
            id="0 reformatted-0 unchanged-4 failed-conditional",
        ),
        pytest.param(
            {"n_reformatted": 1, "n_unchanged": 1, "n_error": 1},
            False,
            [
                "1 file reformatted",
                "1 file left unchanged",
                "1 file failed to reformat",
            ],
            id="1 reformatted-1 unchanged-1 failed",
        ),
        pytest.param(
            {"n_reformatted": 1, "n_unchanged": 1, "n_error": 1},
            True,
            [
                "1 file would be reformatted",
                "1 file would be left unchanged",
                "1 file would fail to reformat",
            ],
            id="1 reformatted-1 unchanged-1 failed-conditional",
        ),
        pytest.param(
            {"n_reformatted": 4, "n_unchanged": 4, "n_error": 4},
            False,
            [
                "4 files reformatted",
                "4 files left unchanged",
                "4 files failed to reformat",
            ],
            id="4 reformatted-4 unchanged-4 failed",
        ),
        pytest.param(
            {"n_reformatted": 4, "n_unchanged": 4, "n_error": 4},
            True,
            [
                "4 files would be reformatted",
                "4 files would be left unchanged",
                "4 files would fail to reformat",
            ],
            id="4 reformatted-4 unchanged-4 failed-conditional",
        ),
    ),
)
def test_report_parts(statistics, conditional, expected):
    r = report.Report(conditional=conditional, **statistics)
    actual = r._report_parts()
    assert actual == expected
