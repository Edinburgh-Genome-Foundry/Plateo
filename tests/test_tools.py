import plateo.tools as tools
import pytest

def invert_sublists(l):
    return [sl[::-1] for sl in l]


@pytest.mark.parametrize("num_wells, expected", [(96, (8, 12)),
                                                 (384, (16, 24)),
                                                 (1536, (32, 48))])
def test_compute_rows_columns(num_wells, expected):
    assert tools.compute_rows_columns(num_wells) == expected


rowname_data = [
    ("A", 1),
    ("E", 5),
    ("AA", 27),
    ("AE", 31)
]

@pytest.mark.parametrize("rowname, expected", rowname_data)
def test_rowname_to_number(rowname, expected):
    assert tools.rowname_to_number(rowname) == expected


@pytest.mark.parametrize("number, expected", invert_sublists(rowname_data))
def test_number_to_rowname(number, expected):
    assert tools.number_to_rowname(number) == expected


coordinates_data = [
    ("A1", (1, 1)),
    ("C2", (3, 2)),
    ("C04", (3, 4)),
    ("H11", (8, 11)),
    ("AA7", (27, 7)),
    ("AC07", (29, 7))
]

@pytest.mark.parametrize("wellname, expected", coordinates_data)
def test_wellname_to_coordinates(wellname, expected):
    assert tools.wellname_to_coordinates(wellname) == expected


coord_to_name_data = [
    ((1, 1), "A1"),
    ((3, 2), "C2"),
    ((3, 4), "C4"),
    ((8, 11), "H11"),
    ((27, 7), "AA7"),
    ((29, 7), "AC7")
]


@pytest.mark.parametrize("coords, expected", coord_to_name_data)
def test_coordinates_to_wellname(coords, expected):
    assert tools.coordinates_to_wellname(coords) == expected

wellname_data = [
    ("A5", 96, "row", 5),
    ("A5", 96, "column", 33),
    ("C6", 96, "row", 30),
    ("C6", 96, "column", 43),
    ("C6", 384, "row", 54),
    ("C6", 384, "column", 83)
]
inverted_wellname_data = [[s[-1], s[1], s[2], s[0]] for s in wellname_data]


@pytest.mark.parametrize("wellname, nwells, direction, expected",
                         wellname_data)
def test_wellname_to_index(wellname, nwells, direction, expected):
    assert tools.wellname_to_index(wellname, nwells, direction) == expected


@pytest.mark.parametrize("index, num_wells, direction, expected",
                         inverted_wellname_data)
def test_index_to_wellname(index, num_wells, direction, expected):
    assert tools.index_to_wellname(index, num_wells, direction) == expected

shift_data = [
    ("A1", 0, 0, "A1"),
    ("A1", 0, 3, "A4"),
    ("A1", 3, 0, "D1"),
    ("A1", 3, 3, "D4"),
    ("Z16", 3, 3, "AC19")
]


@pytest.mark.parametrize("wellname, row_shift, column_shift, expected",
                         shift_data)
def test_shift_wellname(wellname, row_shift, column_shift, expected):
    assert tools.shift_wellname(wellname, row_shift, column_shift) == expected


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
    assert tools.infer_plate_size_from_wellnames(wellnames) == expected
