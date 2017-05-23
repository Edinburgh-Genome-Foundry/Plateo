from copy import deepcopy

from .plate_to_tables import plate_to_pandas_dataframe
from ..tools import number_to_rowname


def plate_to_genesift_sequencing_order_spreadsheet(plate, output_file,
                                                   sample_name_function,
                                                   well_filter=None,
                                                   direction='row'):
    """Generate an excel spreadsheet for ordering through Genesift

    Parameters
    ----------

    plate

    output_file

    sample_name_function
      A function  f(well) => Sample name

    well_filter
      A function  f(well) => True/false

    Example:
    --------

    >>> plate_to_genesift_sequencing_order_spreadsheet(
            plate,
            output_file="genesift.xls",
            sample_name_function= lambda well: data['part_name'] ,
            well_filter=lambda well: data.get('part_name', False)
            direction='column')

    """
    if well_filter is None:
        well_filter = lambda w: True
    
    new_plate = deepcopy(plate)
    def position_function(well):
        return number_to_rowname(well.row) + "%02d" % well.column
    def sample_function(well):
        return sample_name_function(well) if well_filter(well) else None
    new_plate.compute_data_field("Position", position_function)
    new_plate.compute_data_field("Sample", sample_function)
    dataframe = plate_to_pandas_dataframe(new_plate, direction=direction)
    dataframe = dataframe[["Position", "Sample"]]
    dataframe = dataframe[[(e is not None) for e in dataframe['Sample']]]
    dataframe.to_excel(output_file, index=False)
