import pytest

from blackdoc import classification, formats
from blackdoc.tests import data
from blackdoc.tests.data import print_classification, to_classification_format


@pytest.mark.parametrize("format", ("rst", "doctest", "ipython"))
def test_detect_format(format, monkeypatch):
    module = getattr(formats, format)
    detection_funcs = {
        format: module.detection_func,
        "none": formats.none.detection_func,
    }
    monkeypatch.setattr(classification, "detection_funcs", detection_funcs)

    data_module = getattr(data, format)
    expected = to_classification_format(data_module.labels, data_module.lines)
    lines = enumerate(data_module.lines, start=1)
    actual = tuple(classification.detect_format(lines))

    print_classification(actual)

    assert expected == actual
