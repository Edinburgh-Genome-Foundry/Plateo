from collections import OrderedDict
import json
import pandas

#import parsers
#import exporters
from .tools import compute_rows_columns, coordinates_to_wellname

class Well:
    def __init__(self, plate, row, column, name, volume=0, content=None,
                 metadata=None):
        self.plate = plate
        self.row = row
        self.column = column
        self.name = name
        self.volume = volume
        self.content = {} if content is None else content
        self.metadata = {} if metadata is None else metadata

    def transfer_to_other_well(self, destination_well, transfer_volume):
        factor = float(transfer_volume) / self.volume
        quantities_transfered = {
            component: quantity * factor
            for component, quantity in self.content.items()
        }
        self.volume -= transfer_volume
        destination_well.volume += transfer_volume
        destination_well.add_components(quantities_transfered)
        self.subtract_components(quantities_transfered)


    def add_components(self, components_quantities):
        for component, quantity in components_quantities.items():
            if component not in self.content:
                self.content[component] = 0
            self.content[component] += quantity

    def subtract_components(self, components_quantities):
        for component, quantity in components_quantities.items():
            self.content[component] -= quantity

    def __str__(self):
        return "(%s-%s)" % (self.plate.name, self.name)

    def pretty_summary(self):
        metadata = "\n    ".join([""] + [("%s: %s" % (key, value))
                                 for key, value in self.metadata.items()])
        content = "\n    ".join([""] + [("%s: %s" % (key, value))
                                for key, value in self.content.items()])
        return (
            "{self}\n"
            "  Volume: {self.volume}\n"
            "  Content: {content}\n"
            "  Metadata: {metadata}"
        ).format(self=self, content=content, metadata=metadata)




class PlateLayout:

    ALLOWED_SIZES = [96, 384, 1536]

    def __init__(self, num_wells=96, name=None, wells_metadata=None,
                 metadata=None):

        if num_wells not in PlateLayout.ALLOWED_SIZES:
            raise ValueError(
                "Argument num_wells (%s) should be in %s" % (
                str(num_wells), str(PlateLayout.ALLOWED_SIZES))
            )
        self.metadata = {} if metadata is None else metadata
        self.wells_metadata = {} if wells_metadata is None else wells_metadata
        self.name = name
        self.num_wells = num_wells
        self.num_rows, self.num_columns = compute_rows_columns(num_wells)
        self.wells = OrderedDict([])
        for row in range(1, self.num_rows+1):
            for column in range(1,self.num_columns+1):
                wellname = coordinates_to_wellname((row, column))
                meta = self.wells_metadata.get(wellname, {})
                self.wells[wellname] = Well(plate=self, row=row, column=column,
                                            name=wellname, metadata=meta)


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
        """Run fun(well) for every `name:well` in `self.wells_dict`"""
        for wellname, well in self.wells.items():
            fun(well)

    def find_unique_well(self, content_includes=None, condition=None):
        if content_includes is not None:
            condition = lambda well: (content_includes in well.content.keys())
        wells = [
            well
            for name, well in self.wells.items()
            if condition(well)
        ]
        if len(wells)>1:
            raise ValueError("Query returned several wells: %s" % wells)
        elif len(wells)==0:
            raise ValueError("No wells found matching the condition")
        return wells[0]




    def to_pandas_dataframe(self, fields=None, droped_fields=("row", "column")):
        """Return a dataframe with the info on each well"""
        dataframe = pandas.DataFrame.from_dict(self.wells, orient="index")
        dataframe = dataframe.sort_values(by=["row", "column"])
        if len(droped_fields) > 0:
            dataframe = dataframe.drop(droped_fields)
        if fields is not None:
            dataframe = dataframe[fields]
        return dataframe


    def to_bokeh_figure(self, hover_metadata=(), well_to_html=None,
                        well_color_function=None):
        return exporters.plate_to_bokeh_plot(
           self, hover_metadata=hover_metadata,
           well_to_html=well_to_html,
           well_color_function=well_color_function)

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
