"""Read a .gwl picklist"""

import pandas
from ..tools import index_to_wellname
from ..PickList import PickList

def picklist_from_tecan_evo_picklist_file(filename, plates_dict):
    """Read a .gwl file into a PickList

    Parameters
    ----------

    filename
      A .gwl file

    plates_dict
      A dictionnary linking the plate names inside the file to plate objects
      For instance { "PrimersPlate": primers_plate, "SeqDestPlate": ... }

    """
    df = pandas.read_csv(filename, sep=";", header=None)
    df.columns = [
        "Action", "RackLabel", "RackID", "RackType",
        "Position", "TubeID", "Volume", "LiquidClass",
        "TipType", "TipMask"
    ]

    picklist = PickList()
    for i, row in df.iterrows():
        if row.Action == "A":
            source_plate = plates_dict[row.RackLabel]
            source_well_name = index_to_wellname(
                int(row.Position), num_wells=source_plate.num_wells,
                direction="column"
            )
            source_well = source_plate[source_well_name]
        if row.Action == "D":
            dest_plate = plates_dict[row.RackLabel]
            dest_well_name = index_to_wellname(
                int(row.Position), num_wells=dest_plate.num_wells,
                direction="column"
            )
            dest_well = dest_plate[dest_well_name]
            picklist.add_transfer(source_well, dest_well,
                                  volume=float(row.Volume))
    return picklist
