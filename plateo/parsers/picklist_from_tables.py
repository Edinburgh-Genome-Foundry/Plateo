import pandas

from plateo.containers.helper_functions import infer_plate_size_from_wellnames
from ..containers import get_plate_class
from ..transfers.PickList import PickList
from ..transfers.Transfer import Transfer

columnnames = ["source_plate", "source_well", "dest_plate", "dest_well", "volume"]
DF_COLUMNS = {name: name for name in columnnames}


def picklist_from_dataframe(dataframe, source_plates, dest_plates, df_columns=None):
    """Create a picklist from a table specifying the transfers."""
    if df_columns is None:
        df_columns = DF_COLUMNS
    # For matching the plates:
    source_plate_lookup = {plate.name: plate for plate in source_plates}
    dest_plate_lookup = {plate.name: plate for plate in dest_plates}

    list_of_transfers = []
    for i, row in dataframe.iterrows():
        transfer = Transfer(
            source_plate_lookup[row[df_columns["source_plate"]]].wells[
                row[df_columns["source_well"]]
            ],
            dest_plate_lookup[row[df_columns["dest_plate"]]].wells[
                row[df_columns["dest_well"]]
            ],
            row[df_columns["volume"]],
        )
        list_of_transfers += [transfer]

    picklist = PickList(transfers_list=list_of_transfers)

    return picklist


def picklist_from_csv_file(
    filename=None, unit=1e-6, source_plates="auto", dest_plates="auto", df_columns=None
):
    # microliter = 1e-6
    # nanoliter = 1e-9
    dataframe = pandas.read_csv(filename)
    if df_columns is None:
        df_columns = DF_COLUMNS

    if source_plates == "auto":
        source_plate_column = df_columns["source_plate"]
        source_plates = []
        for name in dataframe[source_plate_column].unique():
            nwells = infer_plate_size_from_wellnames(
                dataframe[dataframe[source_plate_column] == name][
                    df_columns["source_well"]
                ]
            )
            source_plate = get_plate_class(nwells)()
            source_plate.name = name
            source_plates += [source_plate]
    if dest_plates == "auto":
        dest_plate_column = df_columns["dest_plate"]
        dest_plates = []
        for name in dataframe[dest_plate_column].unique():
            nwells = infer_plate_size_from_wellnames(
                dataframe[dataframe[dest_plate_column] == name][df_columns["dest_well"]]
            )
            dest_plate = get_plate_class(nwells)()
            dest_plate.name = name
            dest_plates += [dest_plate]

    dataframe[df_columns["volume"]] = dataframe[df_columns["volume"]] * unit

    return picklist_from_dataframe(
        dataframe=dataframe,
        source_plates=source_plates,
        dest_plates=dest_plates,
        df_columns=df_columns,
    )
