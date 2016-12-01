from ..tools import infer_plate_size_from_wellnames
import pandas as pd
from plateo.containers import get_plate_class

def plate_from_dataframe(dataframe, wellname_field="wellname",
                         num_wells="infer", metadata=None):
    """Create a plate from a Pandas dataframe where each row contains the
    name of a well and metadata on the well.

    This function is used e.g. in `plate_from_list_spreadsheet`.

    Parameters
    ----------

    dataframe
      A Pandas dataframe

    wellname_field
      The name of the Pandas dataframe column indicating the name of the wells.

    num_wells
      Number of wells in the dataframe to be
    """

    # TODO: infer plate class automatically ?

    dataframe = dataframe.set_index(wellname_field)
    wells_metadata = {
        well: row.to_dict()
        for well, row in dataframe.iterrows()
    }
    if num_wells == "infer":
        num_wells = infer_plate_size_from_wellnames(wells_metadata.keys())
    plate_class = get_plate_class(num_wells=num_wells)
    return plate_class(wells_metadata=wells_metadata, metadata=metadata)


def plate_from_list_spreadsheet(filename, sheetname=0, num_wells="infer",
                                wellname_field="wellname"):
    """Create a plate from a Pandas dataframe where each row contains the
    name of a well and metadata on the well.

    This function is used e.g. in `plate_from_list_spreadsheet`.
    """

    if ".xls" in filename:  # includes xlsx
        dataframe = pd.read_excel(filename, sheetname=sheetname)
    elif filename.endswith(".csv"):
        dataframe = pd.read_csv(filename)
    return plate_from_dataframe(dataframe, wellname_field=wellname_field,
                                num_wells=num_wells,
                                metadata={"filename": filename})


def plate_from_platemap_spreadsheet(filename, metadata_field="info",
                                    num_wells="infer"):
    """Parse spreadsheets representing a plate map."""

    if filename.lower().endswith(".csv"):
        dataframe = pd.read_csv(filename, index_col=0)
    else:
        dataframe = pd.read_excel(filename, index_col=0)
    wells_metadata = {
        row + str(column): {metadata_field: content}
        for column, column_content in dataframe.to_dict().items()
        for row, content in column_content.items()
    }
    if num_wells == "infer":
        num_wells = infer_plate_size_from_wellnames(wells_metadata.keys())
    plate_class = get_plate_class(num_wells=num_wells)
    return plate_class(wells_metadata=wells_metadata,
                       metadata={"file_source": filename})
