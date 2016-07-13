from collections import OrderedDict
import json
import pandas

import parsers
import exporters
from .tools import compute_rows_columns, wellname_to_index, index_to_wellname

class Transfer:

    def __init__(self, volume, source_well=None, destination_well=None,
                 source_name=None, destination_name=None):
        """A tranfer from a source to a destination

        Parameters
        ----------

        volume (L)
        """
        self.volume = volume
        self.source_well = source_well
        self.source_name = source_name
        self.destination_well = destination_well
        self.destination_name = destination_name

    def to_plain_string(self):
        return ("Dispense {self.volume:.02E} L from {self.source_name} "
                "{self.source_well} into {self.destination_name} "
                "{self.destination_well}").format(self=self)


class PickList:

    def __init__(self, transfers_list, source_plate, destination_plate):

        self.transfers_list = transfers_list
        self.source_plate = source_plate
        self.destination_plate = destination_plate

    def to_plain_string(self):
        return "\n".join(
            transfer.to_plain_string()
            for transfer in self.transfers_list
        )

    def to_plain_textfile(self, filename):
        with open(filename, "w+") as f:
            f.write(self.to_plain_string())

    def to_TECAN_picklist_file(self, filename,
                               change_tips_between_dispenses=True):
        columns = [
            "Action", "RackLabel", "RackID", "RackType",
            "Position", "TubeID", "Volume", "LiquidClass",
            "TipType", "TipMask"
        ]

        rows = []
        for transfer in self.transfers_list:
            volume = "%.01f" % (transfer.volume / 1e-6)
            absorb = {
                "Action": "A",
                "RackLabel": transfer.source_name,
                "Position": wellname_to_index(transfer.source_well,
                                              self.source_plate.num_wells,
                                              direction="column"),
                "Volume": volume
            }
            dispense = {
                "Action": "D",
                "RackLabel": transfer.destination_name,
                "Position": wellname_to_index(transfer.destination_well,
                                              self.destination_plate.num_wells,
                                              direction="column"),
                "Volume":  volume
            }
            row = [absorb, dispense]
            if change_tips_between_dispenses:
                row += [{"Action": "W"}]
            rows += row

        df = pandas.DataFrame.from_records(rows, columns=columns)
        df.to_csv(filename, sep=";", header=False, index=False)

    @staticmethod
    def from_plates(source_plate, destination_plate, volume,
                    source_criterion=None,
                    destination_criterion=None, source_direction="row",
                    destination_direction="row"):

        if not hasattr(volume, "__call__"):
            constant_volume = volume
            volume = lambda source_well: constant_volume

        if source_criterion is None:
            source_criterion = lambda well: True
        if destination_criterion is None:
            destination_criterion = lambda well: True

        def destination_wellnames_generator():
            for index in range(1, destination_plate.num_wells+1):
                destination_wellname = index_to_wellname(
                    index, destination_plate.num_wells,
                    direction=destination_direction)
                destination_well = destination_plate[destination_wellname]
                if destination_criterion(destination_well):
                    yield destination_wellname

        destination_wellnames = destination_wellnames_generator()

        transfers_list = []
        for index in range(1, source_plate.num_wells+1):
            source_wellname = index_to_wellname(
                index, source_plate.num_wells, direction=source_direction)
            source_well = source_plate[source_wellname]
            if source_criterion(source_well):
                destination_wellname = destination_wellnames.next()
                transfers_list.append(
                    Transfer(
                        source_wellname,
                        destination_wellname,
                        volume(source_well)
                    )
                )

        return PickList(transfers_list, source_plate, destination_plate)
