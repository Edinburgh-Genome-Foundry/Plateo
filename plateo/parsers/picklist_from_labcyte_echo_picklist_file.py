import pandas
from ..tools import infer_plate_size_from_wellnames
from ..containers import get_plate_class
from ..PickList import PickList, Transfer

def picklist_from_labcyte_echo_picklist_file(filename=None, dataframe=None,
                                             source_plate="auto",
                                             dest_plate="auto"):
    """Return a Picklist from an ECHO picklist file.

    Parameters
    ----------

    filename
      Path to a .csv or .xls(x) file containing a valid ECHO cherrypick list.

    dataframe
      Dataframe obtained by reading a valid ECHO picklist, which can be
      provided instead of ``filename``.

    source_plate, dest_plate
      Plate objects representing the Source and Destination of the picklist.
      If none is provided, new plates will be created, with sizes inferred
      from the content of the picklist.
    """
    if dataframe is None:
        if filename.lower().endswith(".csv"):
            dataframe = pandas.read_csv(filename)
        else:
            dataframe = pandas.read_excel(filename)
    if source_plate == "auto":
        nwells = infer_plate_size_from_wellnames(dataframe["Source Well"])
        source_plate = get_plate_class(nwells)()
        source_plate.name = "Source"
    if dest_plate == "auto":
        nwells = infer_plate_size_from_wellnames(dataframe["Destination Well"])
        dest_plate = get_plate_class(nwells)()
        dest_plate.name = "Destination"
    return PickList([
        Transfer(source_plate.wells[row["Source Well"]],
                 dest_plate.wells[row["Destination Well"]],
                 1e-9 * row["Volume"])
        for i, row in dataframe.iterrows()
    ])
