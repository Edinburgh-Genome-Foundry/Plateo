# pylint: disable=C0330,C0103,E1101,R0913,E0102,R1705,E0401
"""This module implements the Base class for all plates.

See plateo.container for more specific plate subclasses, with
set number of wells, well format, etc.
"""
from collections import OrderedDict
import pandas
from .Well import Well
from .helper_functions import (
    index_to_wellname,
    number_to_rowname,
    wellname_to_index,
    coordinates_to_wellname,
    rowname_to_number,
)
from ..tools import replace_nans_in_dict


class NoUniqueWell(Exception):
    """NoUniqueWell exception class."""


class Plate:
    """Base class for all plates.

    See the builtin_containers for usage classes, such as generic microplate
    classes (Plate96, Plate384, etc).

    :param name: Name or ID of the Plate as it will appear in strings and reports
    :param wells_data: A dict {"A1": {data}, "A2": ...}.
        The format of the data is left free
    :param plate_data: plate data
    """

    num_rows = None
    num_columns = None
    well_class = Well

    def __init__(self, name=None, wells_data=None, plate_data=None):

        self.name = name
        self.data = plate_data or {}
        self.wells_data = wells_data or {}
        self.num_wells = self.num_rows * self.num_columns
        self.wells = {}
        # self.columns = {column: [] for column in range(1, self.num_columns + 1)}
        # self.rows = {number_to_rowname(row): [] for row in range(1, self.num_rows + 1)}
        for row in range(1, self.num_rows + 1):
            for column in range(1, self.num_columns + 1):
                wellname = coordinates_to_wellname((row, column))
                data = self.wells_data.get(wellname, {})
                well = self.well_class(
                    plate=self, row=row, column=column, name=wellname, data=data
                )
                self.wells[wellname] = well

    def __getitem__(self, k):
        """Return e.g. well A1's dict when calling `myplate['A1']`."""
        return self.wells[k]

    def find_unique_well_by_condition(self, condition):
        """Return the unique well of the plate satisfying the condition.

        The ``condition`` method should have a signature of Well=>True/False.

        Raises a NoUniqueWell error if 0 or several wells satisfy the condition.
        """
        wells = [well for name, well in self.wells.items() if condition(well)]
        if len(wells) > 1:
            raise NoUniqueWell("Query returned several wells: %s" % wells)
        if len(wells) == 0:
            raise NoUniqueWell("No wells found matching the condition")
        return wells[0]

    def find_unique_well_containing(self, query):
        """Return the unique well whose content contains the query."""

        def condition(well):
            return query in well.content.quantities.keys()

        return self.find_unique_well_by_condition(condition)

    def list_well_data_fields(self):
        """Return all fields used in well data in the plate."""
        return sorted(list(set(field for well in self for field in well.data.keys())))

    # def return_column(self, column_number):
    #     """Return the list of all wells of the plate in the given column."""
    #     return [self.wells[wellname] for wellname in self.columns[column_number]]

    def list_wells_in_column(self, column_number):
        """Return the list of all wells of the plate in the given column.

        Examples
        --------
        >>> for well in plate.list_wells_in_column(5):
        >>>      print(well.name)
        """
        return [well for well in self.iter_wells() if well.column == column_number]

    # def return_row(self, row):
    #     """Return a list of wellnames for wells a given row.

    #     The `row` can be either a row number (1,2,3) or row letter(s) (A,B,C).
    #     """
    #     if isinstance(row, int):
    #         row = number_to_rowname(row)
    #     return [self.wells[wellname] for wellname in self.rows[row]]

    def list_wells_in_row(self, row):
        """Return the list of all wells of the plate in the given row.

        The `row` can be either a row number (1,2,3) or row letter(s) (A,B,C).

        Examples
        --------
        >>> for well in plate.list_wells_in_row("H"):
        >>>      print(well.name)

        """
        if isinstance(row, str):
            row = rowname_to_number(row)
        return [well for well in self.iter_wells() if well.row == row]

    def list_filtered_wells(self, well_filter):
        """List filtered wells.

        Examples
        --------
        >>> def condition(well):
        >>>     return well.volume > 50
        >>> for well in myplate.list_filtered_wells(well_filter):
        >>>     print( well.name )
        """
        return list(filter(well_filter, self.wells.values()))

    def wells_grouped_by(
        self,
        data_field=None,
        key=None,
        sort_keys=False,
        ignore_none=False,
        direction_of_occurence="row",
    ):
        """Return wells grouped by key."""
        if key is None:

            def key(well):
                return well.data.get(data_field, None)

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

    def get_well_at_index(self, index, direction="row"):
        """Return the well at the corresponding index.

        Examples
        --------
        >>> plate.get_well_at_index(1)  # well A1
        >>> plate.get_well_at_index(2)  # well A2
        >>> plate.get_well_at_index(2, direction="column")  # well B1
        """
        return self[self.index_to_wellname(index, direction=direction)]

    def index_to_wellname(self, index, direction="row"):
        """Return the name of the well at the corresponding index.

        Examples
        --------
        >>> plate.index_to_wellname(1)  # "A1"
        >>> plate.get_well_at_index(2)  # "A2"
        >>> plate.get_well_at_index(2, direction="column")  # "B1"
        """
        return index_to_wellname(index, self.num_wells, direction=direction)

    def wellname_to_index(self, wellname, direction="row"):
        """Return the index of the well in the plate.

        Examples
        --------
        >>> plate.wellname_to_index("A1")  # 1
        >>> plate.wellname_to_index("A2")  # 2
        >>> plate.wellname_to_index("A1", direction="column")  # 9 (8x12 plate)
        """
        return wellname_to_index(wellname, self.num_wells, direction=direction)

    def wells_sorted_by(self, sortkey):
        """Return wells sorted by sortkey."""
        return (e for e in sorted(self.wells.values(), key=sortkey))

    def iter_wells(self, direction="row"):
        """Iter through the wells either by row or by column.

        Examples
        --------
        >>> for well in plate.iter_wells():
        >>>     print (well.name)
        """
        if direction == "row":
            return self.wells_sorted_by(lambda w: (w.row, w.column))
        else:
            return self.wells_sorted_by(lambda w: (w.column, w.row))

    def __iter__(self):
        """Allow to iter through the well dicts using `for well in myplate`"""
        return self.iter_wells()

    def to_dict(self, replace_nans_by="null"):
        """Convert plate to dict."""
        dct = {
            "data": self.data,
            "wells": {well.name: well.to_dict() for well in self.wells.values()},
        }
        if replace_nans_by is not None:
            replace_nans_in_dict(dct, replace_by=replace_nans_by)
        return dct

    def to_pandas_dataframe(self, fields=None, direction="row"):
        """Return a dataframe with the info on each well."""
        dataframe = pandas.DataFrame.from_records(self.to_dict()["wells"]).T
        by = ["row", "column"] if direction == "row" else ["column", "row"]
        dataframe = dataframe.sort_values(by=by)
        if fields is not None:
            dataframe = dataframe[fields]
        return dataframe

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.name)

    ##########

    def merge_data_from(self, other_plate, overwrite=True):
        """Adds a new field `field_name` to the

        Note that `fun` can also return nothing and simply transform the wells.
        """
        for well in self:
            if well.name in other_plate.wells.keys():
                other_well = other_plate[well.name]
                other_data = other_well.data
                if not overwrite:
                    other_data = {
                        k: v for (k, v) in other_data.items() if k not in well.data
                    }
                well.data.update(other_data)

    def apply_to_wells(self, fun):
        """Run fun(well) for every `name:well` in `self.wells_dict`"""
        for well in self:
            fun(well)

    def compute_data_field(self, field_name, fun, ignore_none=False):
        for well in self:
            data = fun(well)
            if (data is not None) or (not ignore_none):
                well.data[field_name] = data

    def list_data_field_values(self, data_field, include_none=False):
        return list(
            set(
                [
                    w.data[data_field]
                    for w in self.iter_wells()
                    if data_field in w.data
                    and (include_none or (w.data[data_field] is not None))
                ]
            )
        )

    def last_nonempty_well(self, direction="row"):
        """Return the last non-empty well found when traversing the plate."""
        selected_well = None
        for well in self.iter_wells(direction=direction):
            if not well.is_empty:
                selected_well = well
        return selected_well
