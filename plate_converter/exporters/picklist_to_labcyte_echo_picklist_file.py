import pandas as pd
from ..tools import wellname_to_index

def picklist_to_labcyte_echo_picklist_file(picklist, filename, separator=",",
                                           use_well_name=True,
                                           max_single_dispense=5e-7):
    """Write a CSV file for cherrypicking in the ECHO"""
    columns = ["Source Well", "Destination Well", "Transfer Volume"]

    transfers = []
    for trf in picklist.transfers_list:
        n_additional_dispense = int(trf.volume / max_single_dispense)
        rest = trf.volume - n_additional_dispense * max_single_dispense
        for i in range(n_additional_dispense):
            transfers.append(trf.change_volume(max_single_dispense))
        if rest > 0:
            transfers.append(trf.change_volume(rest))

    def format_well(well_name, num_wells):
        if use_well_name:
            return well_name
        else:
            return wellname_to_index(
                well_name,
                num_wells,
                direction="column"
            )
    rows = [
        {
            "Source Well": format_well(
                transfer.source_well.name,
                transfer.source_well.plate.num_wells
            ),
            "Destination Well": format_well(
                transfer.destination_well.name,
                transfer.destination_well.plate.num_wells
            ),
            "Transfer Volume": "%.01f" % (transfer.volume / 1e-9)
        }
        for transfer in transfers
    ]
    df = pd.DataFrame.from_records(rows, columns=columns)
    df.to_csv(filename, sep=separator, header=True, index=False)
