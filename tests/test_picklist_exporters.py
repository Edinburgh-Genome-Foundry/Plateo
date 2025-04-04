import filecmp
import os

from plateo import PickList
from plateo.containers import Plate96
from plateo.exporters import (
    picklist_to_tecan_evo_picklist_file,
    picklist_to_labcyte_echo_picklist_file,
)

data_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.path.join("data", "exporters")
)


# Will be refactored with Dioscuri:
def test_picklist_to_tecan_evo_picklist_file():
    picklist_to_tecan_evo_picklist_file
    pass


def test_picklist_to_labcyte_echo_picklist_file(tmpdir):
    # From examples:
    source_plate = Plate96(name="Source")
    destination_plate = Plate96(name="Destination")
    picklist = PickList()

    picklist.add_transfer(
        source_well=source_plate.wells["A1"],
        destination_well=destination_plate.wells["A5"],
        volume=100e-9,  # 100 nanoliter
    )
    picklist.add_transfer(
        source_well=source_plate.wells["C5"],
        destination_well=destination_plate.wells["A5"],
        volume=100e-9,  # 100 nanoliter
    )
    picklist.add_transfer(
        source_well=source_plate.wells["D6"],
        destination_well=destination_plate.wells["B1"],
        volume=100e-9,  # 100 nanoliter
    )
    picklist_to_labcyte_echo_picklist_file(
        picklist, os.path.join(tmpdir, "my_picklist.csv")
    )
    assert filecmp.cmp(
        os.path.join(tmpdir, "my_picklist.csv"),
        os.path.join(data_dir, "my_picklist.csv"),
    )
