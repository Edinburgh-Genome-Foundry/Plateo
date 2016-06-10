from collections import OrderedDict
import json
import pandas

import parsers
import exporters
from .tools import compute_rows_columns, coordinates_to_wellname

class PlateLayout:

    ALLOWED_SIZES = [96, 384, 1536]

    def __init__(self, num_wells=96, wells_dict=None, name=None, metadata=None):

        if num_wells not in PlateLayout.ALLOWED_SIZES:
            raise ValueError(
                "Argument num_wells (%s) should be in %s" % (
                str(num_wells), str(PlateLayout.ALLOWED_SIZES))
            )
        if metadata is None:
            metadata = {}
        self.metadata = metadata
        self.name = name
        self.wells_dict = wells_dict
        self.num_wells = num_wells
        self.num_rows, self.num_columns = compute_rows_columns(num_wells)
        self.wells = OrderedDict([
            (coordinates_to_wellname((row, column)), {
                "row": row,
                "column": column,
                "well_name": coordinates_to_wellname((row, column))
            })
            for row in range(1, self.num_rows+1)
            for column in range(1,self.num_columns+1)
        ])

        if wells_dict is not None:
            for name, dic in self.wells.items():
                dic.update(wells_dict.get(name, {}))



    def __iter__(self):
        """Allow to iter through the well dicts using `for well in myplate`"""
        return (e for e in self.wells.values())

    def __getitem__(self, k):
        """Return e.g. well A1's dict when calling `myplate['A1']`."""
        return self.wells[k]

    def filter(self, condition):
        return filter(condition, self.wells.values())

    def add_new_field(self, field_name, fun=None, wells=None):
        """Adds a new field `field_name` to the

        Note that `fun` can also return nothing and simply transform the wells.
        """
        if fun is None:
            fun = lambda well: wells[well.well_name]
        for wellname, well in self.wells.items():
            well[field_name] = fun(well)

    def apply_to_wells(self, fun):
        for wellname, well in self.wells.items():
            fun(well)




    def to_pandas_dataframe(self, fields=None, droped_fields=("row", "column")):
        """Return a dataframe with the info on each well"""
        dataframe = pandas.DataFrame.from_dict(self.wells, orient="index")
        dataframe = dataframe.sort_values(by=["row", "column"])
        if len(droped_fields) > 0:
            dataframe = dataframe.drop(droped_fields)
        if fields is not None:
            dataframe = dataframe[fields]
        return dataframe


    def to_bokeh_figure(self, hover_fields=()):
        return exporters.bokeh_plot_plate(
            self.num_wells, self.wells.values(), hover_fields=hover_fields)

    def to_maplotlib_plot(self, statistic, ax=None, mode="text",
                          fontsize=8, colorbar=True):
        """

        Parameters
        ----------

        type
          color or text


        """
        return exporters.plot_plate_statistic_matplotlib(
            self, statistic, ax=ax, mode=mode, fontsize=fontsize,
            colorbar=colorbar
        )


    def write_pdf_report(self, filename):
        pass

    def pretty_string(self, well_name, indent=2):
        return json.dumps(self[well_name], indent=indent)
