import os

from plateo.parsers import (
    picklist_from_labcyte_echo_logfile,
    picklist_from_tecan_evo_picklist_file,
    picklist_from_csv_file,
)


picklist_table_path = os.path.join("tests", "data", "parsers", "picklist_table.csv")


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
