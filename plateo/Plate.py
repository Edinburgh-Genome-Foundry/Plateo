from collections import OrderedDict, defaultdict
import json
import pandas
from .Well import Well
#import parsers
#import exporters
from .tools import (index_to_wellname, wellname_to_index,
                    coordinates_to_wellname, rowname_to_number)


class Plate:

    PlateWell = Well

    def __init__(self, name=None, wells_metadata=None,
                 metadata=None):

        self.name = name
        self.metadata = {} if metadata is None else metadata
        self.wells_metadata = {} if wells_metadata is None else wells_metadata
        self.num_wells = self.num_rows * self.num_columns
        self.wells = OrderedDict([])

        for row in range(1, self.num_rows + 1):
            for column in range(1, self.num_columns + 1):
                wellname = coordinates_to_wellname((row, column))
                meta = self.wells_metadata.get(wellname, {})
                well = self.PlateWell(plate=self, row=row, column=column,
                                      name=wellname, metadata=meta)
                self.wells[wellname] = well

    def __getitem__(self, k):
        """Return e.g. well A1's dict when calling `myplate['A1']`."""
        return self.wells[k]

    def merge_metadata_from(self, other_plate, overwrite=True):
        """Adds a new field `field_name` to the

        Note that `fun` can also return nothing and simply transform the wells.
        """
        for well in self:
            if well.name in other_plate.wells.keys():
                other_well = other_plate[well.name]
                other_metadata = other_well.metadata
                if not overwrite:
                    other_metadata = {k: v for (k, v) in other_metadata.items()
                                      if k not in well.metadata}
                well.metadata.update(other_metadata)

    def apply_to_wells(self, fun):
        """Run fun(well) for every `name:well` in `self.wells_dict`"""
        for well in self:
            fun(well)

    def compute_metadata_field(self, field_name, fun, ignore_none=False):
        for well in self:
            data = fun(well)
            if (data is not None) or (not ignore_none):
                well.metadata[field_name] = data

    def find_unique_well(self, content_includes=None, condition=None):
        if content_includes is not None:
            def condition(well):
                return (content_includes in well.content.quantities.keys())
        wells = [
            well
            for name, well in self.wells.items()
            if condition(well)
        ]
        if len(wells) > 1:
            raise ValueError("Query returned several wells: %s" % wells)
        elif len(wells) == 0:
            raise ValueError("No wells found matching the condition")
        return wells[0]

    def to_pretty_string(self, well_name, indent=2):
        return json.dumps(self[well_name], indent=indent)

    def list_well_metadata_fields(self):
        return sorted(list(set(
            field
            for well in self
            for field in well.metadata.keys()
        )))

    def wells_in_column(self, column_number):
        """Return the list of all wells of the plate in the given column."""
        # TODO: at some point, avoid iterating over all wells, make it smarter
        return [
            well for well in self
            if well.column == column_number
        ]

    def wells_in_row(self, row):
        """Return the list of all wells of the plate in the given row.

        The `row` can be either a row number (1,2,3) or row letter(s) (A,B,C).
        """
        if isinstance(row, str):
            row = rowname_to_number(row)
        return [
            well for well in self
            if well.row == row
        ]

    def wells_satisfying(self, condition):
        """

        Examples
        ---------
        >>> def condition(well):
        >>>     return well.volume > 50
        >>> for well in myplate.wells_satifying(condition):
        >>>     print( well.name )
        """
        return filter(condition, self.wells.values())

    def wells_grouped_by(self, metadata_field=None, key=None, sort_keys=False,
                         ignore_none=False, direction_of_occurence="row"):
        if key is None:
            def key(well):
                return well.metadata.get(metadata_field, None)
        dct = OrderedDict()
        for well in self.iter_wells(direction=direction_of_occurence):
            well_key = key(well)
            if well_key not in dct:
                dct[well_key] = [well]
            else:
                dct[well_key].append(well)
        if ignore_none:
            dct.pop(None, None)
        keys = dct.keys()
        if sort_keys:
            keys = sorted(keys)
        return [(k, dct[k]) for k in keys]

    def get_well_from_index(self, index, direction="row"):
        return self[self.index_to_wellname(index, direction=direction)]

    def well_at_index(self, index, direction="row"):
        return self[self.index_to_wellname(index, direction=direction)]

    def index_to_wellname(self, index, direction="row"):
        return index_to_wellname(index, self.num_wells, direction=direction)

    def wellname_to_index(self, wellname, direction="row"):
        return wellname_to_index(wellname, self.num_wells, direction=direction)

    def iter_wells(self, direction="row"):
        """Iter through the wells either by row or by column"""
        if direction == "row":
            return self.wells_sorted_by(lambda w: (w.row, w.column))
        else:
            return self.wells_sorted_by(lambda w: (w.column, w.row))

    def wells_sorted_by(self, sortkey):
        return (e for e in sorted(self.wells.values(), key=sortkey))

    def __iter__(self):
        """Allow to iter through the well dicts using `for well in myplate`"""
        return self.iter_wells()

    def to_dict(self):
        return {
            "metadata": self.metadata,
            "wells": {
                well.name: well.to_dict()
                for well in self
            }
        }

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.name)
