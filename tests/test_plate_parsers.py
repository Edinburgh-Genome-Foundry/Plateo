import os

import pytest

from plateo.Plate import Plate
from plateo.parsers import (
    plate_from_platemap_spreadsheet,
    plate_from_list_spreadsheet,
    plate_from_nanodrop_xml_file,
    plate_from_aati_fragment_analyzer_peaktable,
    plate_from_aati_fragment_analyzer_zip,
    plate_from_dataframe,
)


def test_plate_from_platemap_spreadsheet():
    plate_from_platemap_spreadsheet
    pass


def test_plate_from_list_spreadsheet():
    plate_from_list_spreadsheet
    pass


def test_plate_from_nanodrop_xml_file():
    plate_from_nanodrop_xml_file
    pass


def test_plate_from_dataframe():
    plate_from_dataframe
    pass


def test_plate_from_aati_fragment_analyzer_peaktable(tmpdir):
    data_path = os.path.join("tests", "data")
    peaktable = os.path.join(data_path, "example_Peak Table.csv")
    plate = plate_from_aati_fragment_analyzer_peaktable(peaktable)
    assert isinstance(plate, Plate)

    bad_peaktable = os.path.join(data_path, "example_BAD_Peak Table.csv")
    with pytest.raises(Exception):
        plate_from_aati_fragment_analyzer_peaktable(bad_peaktable)


def test_plate_from_aati_fragment_analyzer_zip():
    plate_from_aati_fragment_analyzer_zip
    pass
