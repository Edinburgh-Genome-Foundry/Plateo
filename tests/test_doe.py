import os

import pandas

from plateo.applications.doe import (
    convert_volumetable_to_actiontable,
    import_volumetable_from_csv_file,
)
from plateo.parsers import plate_from_content_spreadsheet
from plateo.containers import Plate96

volumetable_path = os.path.join("tests", "data", "applications", "volumetable.csv")
source_plate_path = os.path.join("tests", "data", "applications", "Source_Plate.xlsx")


def test_volumetable_from_csv_file():
    assert type(import_volumetable_from_csv_file(volumetable_path)) == pandas.DataFrame


def test_dataframe_from_volume_table():
    volumetable = import_volumetable_from_csv_file(volumetable_path)
    source_plate = plate_from_content_spreadsheet(source_plate_path)
    dest_plate = Plate96(name="dest")
    dataframe = convert_volumetable_to_actiontable(
        volumetable=volumetable, source_plate=source_plate, dest_plate=dest_plate
    )

    assert type(dataframe) == pandas.DataFrame
