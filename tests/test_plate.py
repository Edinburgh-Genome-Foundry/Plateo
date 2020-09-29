import pytest

from plateo.containers.plates import Plate96
from plateo.Well import Well


def condition(well):
    return well.volume > 20 * 10 ** (-6)


def test_find_unique_well_by_condition():
    with pytest.raises(Exception):
        Plate96().find_unique_well_by_condition(condition)


def test_find_unique_well_containing():
    with pytest.raises(Exception):
        Plate96().find_unique_well_containing("testquery")


def test_list_well_data_fields():
    assert Plate96().list_well_data_fields() == []


def test_wells_in_column():
    assert isinstance(Plate96().wells_in_column(5)[0], Well)


def test_wells_in_row():
    assert isinstance(Plate96().wells_in_row(5)[0], Well)


def test_wells_satisfying():
    def condition(well):
        return well.volume > 50

    assert type(Plate96().wells_satisfying(condition)) == filter


def test_wells_grouped_by():
    assert len(Plate96().wells_grouped_by()[0][1]) == 96


def test_get_well_at_index():
    well = Plate96().well_at_index(5)
    assert well.name == "A5"


wellname_data = [
    ("A5", "row", 5),
    ("A5", "column", 33),
    ("C6", "row", 30),
    ("C6", "column", 43),
]
inverted_wellname_data = [[s[-1], s[1], s[0]] for s in wellname_data]


@pytest.mark.parametrize("wellname, direction, expected", wellname_data)
def test_wellname_to_index(wellname, direction, expected):
    assert Plate96().wellname_to_index(wellname, direction) == expected


@pytest.mark.parametrize("index, direction, expected", inverted_wellname_data)
def test_index_to_wellname(index, direction, expected):
    assert Plate96().index_to_wellname(index, direction) == expected


def test_iter_wells():
    result = Plate96().iter_wells()
    assert isinstance(next(result), Well)


def test___repr__():
    assert Plate96().__repr__() == "Plate96(None)"
