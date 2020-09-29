import pytest

from plateo.containers.plates import Plate96
from plateo.Well import TransferError, Well


plate = Plate96()
well = plate.well_at_index(1)


def test_volume():
    assert well.volume == 0


def test_iterate_sources_tree():
    result = well.iterate_sources_tree()
    assert isinstance(next(result), Well)


def test_add_content():
    plate = Plate96()
    well = plate.well_at_index(1)
    components_quantities = {"Compound_1": 5}
    volume = 20 * 10 ** (-6)  # 20 uL
    well.add_content(components_quantities, volume=volume)
    assert well.content.quantities == {"Compound_1": 5}


def test_subtract_content():
    components_quantities = {"Compound_1": 5}
    volume = 30 * 10 ** (-6)  # 30 uL
    with pytest.raises(TransferError):
        well.subtract_content(components_quantities, volume)


def test_empty_completely():
    well.empty_completely()
    assert well.content.volume == 0


def test___repr__():
    assert well.__repr__() == "(None-A1)"


def test_pretty_summary():
    result = well.pretty_summary()
    expected = "(None-A1)\n  Volume: 0\n  Content: \n  Metadata: "
    assert result == expected


def test_to_dict():
    result = well.to_dict()
    expected = {
        "name": "A1",
        "content": {"volume": 0, "quantities": {}},
        "row": 1,
        "column": 1,
    }
    assert result == expected


def test_index_in_plate():
    result = well.index_in_plate()
    expected = 1
    assert result == expected


other_well = plate.well_at_index(2)


def test_is_after():
    assert well.is_after(other_well) is False
    assert other_well.is_after(well) is True


def test___lt__():
    assert True
