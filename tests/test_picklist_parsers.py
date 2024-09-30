import os

from plateo.parsers import (
    picklist_from_labcyte_echo_logfile,
    picklist_from_tecan_evo_picklist_file,
    picklist_from_csv_file,
)


picklist_table_path = os.path.join("tests", "data", "parsers", "picklist_table.csv")
picklist_table_path_columns = os.path.join(
    "tests", "data", "parsers", "picklist_table_columns.csv"
)


def test_picklist_from_labcyte_echo_logfile():
    picklist_from_labcyte_echo_logfile
    pass


def test_picklist_from_tecan_evo_picklist_file():
    picklist_from_tecan_evo_picklist_file
    pass


def test_picklist_from_csv_file():
    picklist = picklist_from_csv_file(picklist_table_path)
    assert (
        picklist.to_plain_string()
        == "Transfer 1.00E-06L from source A1 into destination B2"
    )

    # User-defined dataframe columns:
    user_columns = {
        "source_plate": "Source Plate",
        "source_well": "Source Well",
        "dest_plate": "Destination Plate",
        "dest_well": "Destination Well",
        "volume": "Volume",
    }

    picklist = picklist_from_csv_file(
        picklist_table_path_columns, df_columns=user_columns
    )
    assert (
        picklist.to_plain_string()
        == "Transfer 3.00E-06L from source A8 into destination C4"
    )
