from collections import OrderedDict
from copy import deepcopy
import json

import pandas

#import parsers
#import exporters
from .tools import compute_rows_columns, wellname_to_index, index_to_wellname



class Transfer:

    def __init__(self, source_well, destination_well, volume, metadata=None):
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
        return Transfer(source_well=self.source_well,
                        destination_well=self.destination_well,
                        volume=new_volume,
                        metadata=self.metadata)


class PickList:

    def __init__(self, transfers_list=(), metadata=None):

        self.transfers_list = list(transfers_list)
        self.metadata = {} if metadata is None else metadata

    def add_transfer(self, source_well=None, destination_well=None,
                     volume=None,  metadata=None, transfer=None):
        if transfer is None:
            transfer = Transfer(source_well=source_well,
                                destination_well=destination_well,
                                volume=volume,
                                metadata=metadata)
        self.transfers_list.append(transfer)

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

    def execute(self, content_field="content", inplace=True,
                callback_function=None):

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
            new_picklist.execute(content_field=content_field, inplace=True,
                                 callback_function=callback_function)
            return new_plates

        else:
            for transfer in self.transfers_list:
                transfer.source_well.transfer_to_other_well(
                    destination_well=transfer.destination_well,
                    transfer_volume=transfer.volume)
                if callback_function is not None:
                    callback_function(self, transfer)

    def restricted_to(self, transfer_filter=None, source_well=None,
                      destination_well=None):
        """Return a version of the picklist restricted to transfers with the
        right source/destination well"""
        if transfer_filter is None:
            def transfer_filter(tr):
                source_well_is_ok = ((source_well is None) or
                                     (source_well == tr.source_well))
                dest_well_is_ok = ((destination_well is None) or
                                   (destination_well == tr.destination_well))
                return (source_well_is_ok and dest_well_is_ok)

        transfers = [tr for tr in self.transfers_list if transfer_filter(tr)]
        return PickList(transfers, metadata={"parent": self})

    def sorted_by(self, sorting_method="source_well"):
        if not hasattr(sorting_method, "__call__"):
            def sorting_method(transfer):
                return transfer.__dict__[sorting_method]
        return PickList(sorted(self.transfers_list, key=sorting_method),
                        metadata={"parent": self})

    def split_by(self, prop):
        if isinstance(prop, str):
            str_prop = prop
            def prop(t):
                return t.__dict__[str_prop]
        categories = set([prop(tr) for tr in self.transfers_list])
        return [
            (category, self.restricted_to(lambda tr: prop(tr) == category))
            for category in categories
        ]

    def total_transfered_volume(self):
        return sum([transfer.volume for transfer in self.transfers_list])

    @staticmethod
    def from_plates(source_plate, destination_plate, volume,
                    source_criterion=None,
                    destination_criterion=None, source_direction="row",
                    destination_direction="row"):
        """Create a PickList object based on plates and conditions.

        BROKEN due to changes in picklists. TODO: Fix.
        """

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

    def enforce_maximum_dispense_volume(self, max_dispense_volume):
        """Return a new picklist were every too-large dispense is broken down
        into smaller dispenses."""
        transfers = []
        for trf in self.transfers_list:
            n_additional_dispense = int(trf.volume / max_dispense_volume)
            rest = trf.volume - n_additional_dispense * max_dispense_volume
            for i in range(n_additional_dispense):
                transfers.append(trf.change_volume(max_dispense_volume))
            if rest > 0:
                transfers.append(trf.change_volume(rest))
        return PickList(transfers_list=transfers)

    def __add__(self, other):
        return PickList(self.transfers_list + other.transfers_list)

    @staticmethod
    def merge_picklists(picklists_list):
        """Merge the list of picklists into a single picklist.

        The transfers in the final picklist are the concatenation of the
        tranfers in the different picklists, in the order in which they appear
        in the list.
        """
        return sum(picklists_list, PickList([]))
