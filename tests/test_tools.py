import numpy as np
import plateo.tools as tools
import plateo.containers.helper_functions as helper_functions

import pytest


def test_round_at():
    assert tools.round_at(42.0, None) == 42.0
    assert tools.round_at(6.28318, 10 ** (-2)) == 6.28


def test_dicts_to_columns():
    test_dict = {1: np.nan, 2: {"a": np.nan}}
    tools.replace_nans_in_dict(test_dict)
    expected = {1: "null", 2: {"a": "null"}}
    assert test_dict == expected


def test_human_seq_size():
    assert tools.human_seq_size(42) == "42b"
    tools.human_seq_size(1042) == "1.0k"
    tools.human_seq_size(42000) == "42k"


def test_human_volume():
    assert tools.human_volume(500) == "500 L"


shift_data = [
    ("A1", 0, 0, "A1"),
    ("A1", 0, 3, "A4"),
    ("A1", 3, 0, "D1"),
    ("A1", 3, 3, "D4"),
    ("Z16", 3, 3, "AC19"),
]


@pytest.mark.parametrize("wellname, row_shift, column_shift, expected", shift_data)
def test_shift_wellname(wellname, row_shift, column_shift, expected):
    assert (
        helper_functions.shift_wellname(wellname, row_shift, column_shift) == expected
    )


infer_size_data = [
    [("A1", "D5"), 96],
    [("C10", "E5", "H12"), 96],
    [("C10", "I5"), 384],
    [("C14", "A5"), 384],
    [("AA1", "D5", "H12"), 1536],
    [("A1", "D30"), 1536],
]


@pytest.mark.parametrize("wellnames, expected", infer_size_data)
def test_infer_plate_size_from_wellnames(wellnames, expected):
    """Return the first of 96, 384, or 1536, to contain all wellnames."""
    assert helper_functions.infer_plate_size_from_wellnames(wellnames) == expected
