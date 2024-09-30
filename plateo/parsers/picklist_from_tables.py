import pandas

from plateo.containers.helper_functions import infer_plate_size_from_wellnames
from ..containers import get_plate_class
from ..transfers.PickList import PickList
from ..transfers.Transfer import Transfer

DF_COLUMNS = {
    "source_plate": "source_plate",
    "source_well": "source_well",
    "dest_plate": "dest_plate",
    "dest_well": "dest_well",
    "volume": "volume",
}


def picklist_from_dataframe(dataframe, source_plates, dest_plates):
    # For matching the plates:
    source_plate_lookup = {plate.name: plate for plate in source_plates}
    dest_plate_lookup = {plate.name: plate for plate in dest_plates}

    list_of_transfers = []
    for i, row in dataframe.iterrows():
        transfer = Transfer(
            source_plate_lookup[row[DF_COLUMNS["source_plate"]]].wells[
                row[DF_COLUMNS["source_well"]]
            ],
            dest_plate_lookup[row[DF_COLUMNS["dest_plate"]]].wells[
                row[DF_COLUMNS["dest_well"]]
            ],
            row[DF_COLUMNS["volume"]],
        )
        list_of_transfers += [transfer]

    picklist = PickList(transfers_list=list_of_transfers)

    return picklist


def picklist_from_csv_file(
    filename=None, unit=1e-6, source_plates="auto", dest_plates="auto"
):
    # microliter = 1e-6
    # nanoliter = 1e-9
    dataframe = pandas.read_csv(filename)

    if source_plates == "auto":
        source_plates = []
        for name in dataframe["source_plate"].unique():
            nwells = infer_plate_size_from_wellnames(
                dataframe[dataframe["source_plate"] == name]["source_well"]
            )
            source_plate = get_plate_class(nwells)()
            source_plate.name = name
            source_plates += [source_plate]
    if dest_plates == "auto":
        dest_plates = []
        for name in dataframe["dest_plate"].unique():
            nwells = infer_plate_size_from_wellnames(
                dataframe[dataframe["dest_plate"] == name]["dest_well"]
            )
            dest_plate = get_plate_class(nwells)()
            dest_plate.name = name
            dest_plates += [dest_plate]

    dataframe["volume"] = dataframe["volume"] * unit

    return picklist_from_dataframe(
        dataframe=dataframe, source_plates=source_plates, dest_plates=dest_plates
    )
