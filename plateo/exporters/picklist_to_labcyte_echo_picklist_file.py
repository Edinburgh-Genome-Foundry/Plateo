import pandas as pd
from ..tools import wellname_to_index

def picklist_to_labcyte_echo_picklist_file(picklist, filename,
                                           use_well_name=True,
                                           max_dispense_volume=5e-7):
    """Write a CSV file for cherrypicking in the ECHO.

    Note that transfer volumes may have to be rounded to 2.5nl to be valid.

    Parameters
    -----------

    picklist
      The PickList object to be written in a file.

     filename
       The destination filename or path, e.g. `20160408_picklist.csv`

     use_well_name
       If True, the final file contains wellnames in plain, else the final
       file contains well numbers: A1 is 1, B1 is 2, C1 is 3, etc.

     max_dispense_volume
       Maximal volume that can be dispensed in one go. For the ECHO it may
       be 500nL (default value here)
    """
    
    columns = ["Source Well", "Destination Well", "Transfer Volume"]
    picklist = picklist.enforce_maximum_dispense_volume(max_dispense_volume)

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
        for transfer in picklist.transfers_list
    ]
    df = pd.DataFrame.from_records(rows, columns=columns)
    df.to_csv(filename, sep=",", header=True, index=False)
