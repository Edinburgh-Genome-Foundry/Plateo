import pytest

from plateo import Transfer
from plateo.containers.plates import Plate96
from plateo.Well import TransferError


def test_TransferError():
    with pytest.raises(ValueError):
        raise TransferError()


source = Plate96(name="Source")
destination = Plate96(name="Destination")
source_well = source.wells["A1"]
destination_well = destination.wells["B2"]
volume = 25 * 10 ** (-6)
transfer = Transfer(source_well, destination_well, volume)


def test_to_plain_string():
    assert transfer.to_plain_string() == "2.50E-05L from Source A1 into Destination B2"


def test___repr__():
    assert transfer.__repr__() == "2.50E-05L from Source A1 into Destination B2"
