"""Classes to represent picklists and liquid transfers in general"""
from collections import OrderedDict
from copy import deepcopy
import json

import pandas

#import parsers
#import exporters
from .tools import compute_rows_columns, wellname_to_index, index_to_wellname



class Transfer:
    """A tranfer from a source to a destination

    Parameters
    ----------

    source_well
      A Well object representing the plate well from which to transfer

    destination_well
      A Well object representing the plate well to which to transfer.

    volume
      Volume to be transfered, expressed in liters.

    data
      A dict containing any useful information on the transfer, this
      information can be used later e.g. as parameters for the transfer
      when exporting a picklist.
    """
    def __init__(self, source_well, destination_well, volume, data=None):

        self.volume = volume
        self.source_well = source_well
        self.destination_well = destination_well
        self.data = data

    def to_plain_string(self):
        """Return "xx L from {source_well} into {dest_well}"."""
        return ("{self.volume:.02E}L from {self.source_well.plate.name} "
                "{self.source_well.name} into "
                "{self.destination_well.plate.name} "
                "{self.destination_well.name}").format(
                    self=self
        )

    def change_volume(self, new_volume):
        """Return a version of the transfer with a new volume."""
        return Transfer(source_well=self.source_well,
                        destination_well=self.destination_well,
                        volume=new_volume,
                        data=self.data)


class PickList:
    """Representation of a list of well-to-well transfers.

    Parameters
    -----------

    transfers_list
      A list of Transfer objects that will be part of a same dispensing
      operation, in the order in which they are meant to be executed.

    data
      A dict with some infos on the picklist.

    """

    def __init__(self, transfers_list=(), data=None):

        self.transfers_list = list(transfers_list)
        self.data = {} if data is None else data

    def add_transfer(self, source_well=None, destination_well=None,
                     volume=None,  data=None, transfer=None):
        """Add a transfer to the picklist's tranfers list.

        You can either provide a ``Transfer`` object with the ``transfer``
        parameter, or the parameters


        """
        if transfer is None:
            transfer = Transfer(source_well=source_well,
                                destination_well=destination_well,
                                volume=volume,
                                data=data)
        self.transfers_list.append(transfer)

    def to_plain_string(self):
        """Return the list of transfers in human readable format"""
        return "\n".join(
            transfer.to_plain_string()
            for transfer in self.transfers_list
        )

    def to_plain_textfile(self, filename):
        """Write the picklist in a file in a human reable format."""
        with open(filename, "w+") as f:
            f.write(self.to_plain_string())

    def execute(self, content_field="content", inplace=True,
                callback_function=None):
        """Simulate the execution of the picklist"""

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
        right source/destination well.

        You can provide ``source_well`` and ``destination_well`` or
        alternatively just a function ``transfer_filter`` with signature
        (transfer)=>True/False that will be used to filter out transfers
        (for which it returns false).

        """
        if transfer_filter is None:
            def transfer_filter(tr):
                source_well_is_ok = ((source_well is None) or
                                     (source_well == tr.source_well))
                dest_well_is_ok = ((destination_well is None) or
                                   (destination_well == tr.destination_well))
                return (source_well_is_ok and dest_well_is_ok)

        transfers = [tr for tr in self.transfers_list if transfer_filter(tr)]
        return PickList(transfers, data={"parent": self})

    def sorted_by(self, sorting_method="source_well"):
        """Return a new version of the picklist sorted by some parameter.

        The ``sorting_method`` is either the name of an attribute of the
        transfers, such as "source_well", or a function f(transfer) -> value.
        """
        if not hasattr(sorting_method, "__call__"):
            def sorting_method(transfer):
                return transfer.__dict__[sorting_method]
        return PickList(sorted(self.transfers_list, key=sorting_method),
                        data={"parent": self})

    def split_by(self, category):
        """Split the picklist into a list of picklists, per category.

        The returned list if of the form [(cat, subpicklist)] where
        ``cat`` is the value of the category for all transfers in
        ``subpicklist``.

        The parameter ``category`` is either the name of a transfer attribute
        or a function f(transfer)=> value which is used to
        """
        if isinstance(category, str):
            str_category = category
            def category(t):
                return t.__dict__[str_category]
        categories = set([category(tr) for tr in self.transfers_list])
        return [
            (cat, self.restricted_to(lambda tr: category(tr) == cat))
            for cat in sorted(categories)
        ]

    def total_transfered_volume(self):
        """Return the sum of all volumes from all transfers."""
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
