import filecmp
import os

import pandas

from plateo.applications.doe import (
    import_valuetable_from_csv,
    convert_valuetable_to_volumetable,
    convert_volumetable_to_actiontable,
    import_volumetable_from_csv_file,
)
from plateo.parsers import plate_from_content_spreadsheet
from plateo.containers import Plate96

valuetable_path = os.path.join("tests", "data", "applications", "valuetable.csv")
volumetable_out_path = os.path.join(
    "tests", "data", "applications", "volumetable_out_in_L.csv"
)

volumetable_path = os.path.join("tests", "data", "applications", "volumetable.csv")
source_plate_path = os.path.join("tests", "data", "applications", "Source_Plate.xlsx")


def test_convert_valuetable_to_volumetable(tmpdir):
    source_plate = plate_from_content_spreadsheet(source_plate_path)
    valuetable = import_valuetable_from_csv(valuetable_path)
    volumetable = convert_valuetable_to_volumetable(
        valuetable, source_plate=source_plate
    )
    volumetable.to_csv(
        path_or_buf=os.path.join(tmpdir, "volumetable_out.csv"),
        sep=",",
        columns=None,
        header=True,
        index=True,
        float_format="%.7f",
    )
    assert filecmp.cmp(
        os.path.join(volumetable_out_path),
        os.path.join(tmpdir, "volumetable_out.csv"),
    )


def test_volumetable_from_csv_file():
    assert type(import_volumetable_from_csv_file(volumetable_path)) is pandas.DataFrame


def test_convert_volumetable_to_actiontable():
    volumetable = import_volumetable_from_csv_file(volumetable_path)
    source_plate = plate_from_content_spreadsheet(source_plate_path)
    dest_plate = Plate96(name="dest")
    dataframe = convert_volumetable_to_actiontable(
        volumetable=volumetable, source_plate=source_plate, dest_plate=dest_plate
    )

    assert type(dataframe) is pandas.DataFrame
    assert dest_plate.wells["A1"].data["expunit"] == "unit_1"
