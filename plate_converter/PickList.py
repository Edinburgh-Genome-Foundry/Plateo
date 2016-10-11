from collections import OrderedDict
from copy import deepcopy
import json

import pandas

#import parsers
#import exporters
from .tools import compute_rows_columns, wellname_to_index, index_to_wellname



class Transfer:

    def __init__(self, source_well, destination_well, volume,
                 source_plate=None, destination_plate=None, metadata=None):
        """A tranfer from a source to a destination

        Parameters
        ----------

        volume (L)
        """
        self.volume = volume
        self.source_well = source_well
        self.destination_well = destination_well
        self.metadata = metadata

    def to_plain_string(self):
        return ("{self.volume:.02E}L from {self.source_well.plate.name} "
                "{self.source_well.name} into "
                "{self.destination_well.plate.name} "
                "{self.destination_well.name}").format(
                    self=self
        )

    def change_volume(self, new_volume):
        new = deepcopy(self)
        new.volume = new_volume
        return new


class PickList:

    def __init__(self, transfers_list, metadata=None):

        self.transfers_list = transfers_list
        self.metadata = {} if metadata is None else metadata

    def to_plain_string(self):
        return "\n".join(
            transfer.to_plain_string()
            for transfer in self.transfers_list
        )

    def to_plain_textfile(self, filename):
        with open(filename, "w+") as f:
            f.write(self.to_plain_string())

    def to_json(self):
        return {
            "source_plate": self.source_plate.to_json(),
            "destination_plate": self.destination_plate.to_json(),
            "metadata": self.metadata
        }

    def execute(self, content_field="content", inplace=True):

        if not inplace:
            all_plates = set(
                plate
                for transfer in self.transfers_list
                for plate in [transfer.source_well.plate,
                              transfer.destination_well.plate]
            )
            new_plates = {
                plate: deepcopy(plate)
                for plate in all_plates
            }

            new_transfer_list = []
            for transfer in self.transfers:
                new_source_plate = new_plates[transfer.source_well.plate]
                new_dest_plate = new_plates[transfer.destination_well.plate]
                new_source_well = new_source_plate.wells[
                    transfer.source_well.name]
                new_dest_well = new_dest_plate.wells[
                    transfer.destination_well.name]
                new_transfer_list.append(Transfer(
                    volume=transfer.volume,
                    source_well=new_source_well,
                    destination_well=new_dest_well
                ))

            new_picklist = PickList(transfers_list=new_transfer_list)
            new_picklist.execute(inplace=True)
            return new_plates

        else:
            for transfer in self.transfers_list:
                transfer.source_well.transfer_to_other_well(
                    destination_well=transfer.destination_well,
                    transfer_volume=transfer.volume)

    # def to_TECAN_picklist_file(self, filename,
    #                            change_tips_between_dispenses=True):
    #     columns = [
    #         "Action", "RackLabel", "RackID", "RackType",
    #         "Position", "TubeID", "Volume", "LiquidClass",
    #         "TipType", "TipMask"
    #     ]
    #
    #     rows = []
    #     for transfer in self.transfers_list:
    #         volume = "%.01f" % (transfer.volume / 1e-6)
    #         absorb = {
    #             "Action": "A",
    #             "RackLabel": transfer.source_plate.name,
    #             "Position": wellname_to_index(transfer.source_well,
    #                                           transfer.source_plate.num_wells,
    #                                           direction="column"),
    #             "Volume": volume
    #         }
    #         dispense = {
    #             "Action": "D",
    #             "RackLabel": transfer.destination_plate.name,
    #             "Position": wellname_to_index(transfer.destination_well,
    #                                           self.destination_plate.num_wells,
    #                                           direction="column"),
    #             "Volume":  volume
    #         }
    #         row = [absorb, dispense]
    #         if change_tips_between_dispenses:
    #             row += [{"Action": "W"}]
    #         rows += row
    #
    #     df = pandas.DataFrame.from_records(rows, columns=columns)
    #     df.to_csv(filename, sep=";", header=False, index=False)

    # def to_ECHO_picklist_file(self, filename, separator=",",
    #                           use_well_name=True, max_single_dispense=5e-7):
    #     """Write a CSV file for cherrypicking in the ECHO"""
    #     columns = ["Source Well", "Destination Well", "Transfer Volume"]
    #
    #     transfers = []
    #     for trf in self.transfers_list:
    #         n_additional_dispense = int(trf.volume / max_single_dispense)
    #         rest = trf.volume - n_additional_dispense * max_single_dispense
    #         for i in range(n_additional_dispense):
    #             transfers.append(trf.change_volume(max_single_dispense))
    #         if rest > 0:
    #             transfers.append(trf.change_volume(rest))
    #
    #     def format_well(well_name, num_wells):
    #         if use_well_name:
    #             return well_name
    #         else:
    #             return wellname_to_index(
    #                 well_name,
    #                 num_wells,
    #                 direction="column"
    #             )
    #     rows = [
    #         {
    #             "Source Well": format_well(
    #                 transfer.source_well.name,
    #                 transfer.source_well.plate.num_wells
    #             ),
    #             "Destination Well": format_well(
    #                 transfer.destination_well.name,
    #                 transfer.destination_well.plate.num_wells
    #             ),
    #             "Transfer Volume": "%.01f" % (transfer.volume / 1e-9)
    #         }
    #         for transfer in transfers
    #     ]
    #     df = pandas.DataFrame.from_records(rows, columns=columns)
    #     df.to_csv(filename, sep=separator, header=True, index=False)

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
            for index in range(1, destination_plate.num_wells + 1):
                destination_wellname = index_to_wellname(
                    index, destination_plate.num_wells,
                    direction=destination_direction)
                destination_well = destination_plate[destination_wellname]
                if destination_criterion(destination_well):
                    yield destination_wellname

        destination_wellnames = destination_wellnames_generator()

        transfers_list = []
        for index in range(1, source_plate.num_wells + 1):
            source_wellname = index_to_wellname(
                index, source_plate.num_wells, direction=source_direction)
            source_well = source_plate[source_wellname]
            if source_criterion(source_well):
                destination_wellname = destination_wellnames.next()
                transfers_list.append(
                    Transfer(
                        source_well=source_wellname,
                        destination_well=destination_wellname,
                        volume=volume(source_well),
                        source_plate=source_plate,
                        destination_plate=destination_plate
                    )
                )

        return PickList(transfers_list)
