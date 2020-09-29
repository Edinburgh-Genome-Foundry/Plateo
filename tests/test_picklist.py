import os
import pytest

from plateo import Transfer, PickList
from plateo.containers.plates import Plate96


source = Plate96(name="Source")
destination = Plate96(name="Destination")
source_well = source.wells["A1"]
destination_well = destination.wells["B2"]
volume = 25 * 10 ** (-6)
transfer_1 = Transfer(source_well, destination_well, volume)
picklist = PickList()


def test_add_transfer():
    picklist.add_transfer(transfer=transfer_1)
    assert isinstance(picklist.transfers_list[0], Transfer)


def test_to_plain_string():
    assert picklist.to_plain_string() == "2.50E-05L from Source A1 into Destination B2"


def test_to_plain_textfile(tmpdir):
    path = os.path.join(str(tmpdir), "test.txt")
    picklist.to_plain_textfile(filename=path)
    assert os.path.exists(path)


def test_execute():
    with pytest.raises(ValueError):
        picklist.execute(inplace=False)


def test_restricted_to():
    new_picklist = picklist.restricted_to(
        source_well=destination_well, destination_well=destination_well
    )
    assert len(new_picklist.transfers_list) == 0

    new_picklist_2 = picklist.restricted_to(
        source_well=source_well, destination_well=destination_well
    )
    assert len(new_picklist_2.transfers_list) == 1


def test_sorted_by():
    assert isinstance(PickList().sorted_by(), PickList)


def test_total_transfered_volume():
    assert picklist.total_transfered_volume() == 25 * 10 ** (-6)


def test_enforce_maximum_dispense_volume():
    new_picklist = picklist.enforce_maximum_dispense_volume(5 * 10 ** (-6))
    assert len(new_picklist.transfers_list) == 5


def test_merge_picklists():
    new_picklist = picklist.merge_picklists([picklist, picklist])
    assert len(new_picklist.transfers_list) == 2
