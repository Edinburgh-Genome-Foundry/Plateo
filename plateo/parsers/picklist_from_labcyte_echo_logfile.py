from ..PickList import PickList, Transfer
from ..Plate import Plate

import pandas as pd
import sys
PYTHON3 = (sys.version_info[0] == 3)

if PYTHON3:
    from io import StringIO
else:
    from StringIO import StringIO

def picklist_from_labcyte_echo_logfile(filename=None, filecontent=None,
                                       plates_dict={}):
    """Return a picklist of what was actually dispensed in the ECHO, based
    on the log file.

    Picklist.metadata["exceptions"] is a picklist of all transfers that went
    wrong.

    """

    if filename is not None:
        with open(filename) as f:
            filecontent = f.read()

    def read_key_value_block(block, target_dict):
        for line in block.splitlines():
            key, value = line.split(",")
            target_dict[key] = value

    def block_to_transfers_list(block):
        block = "\n".join(block.splitlines()[1:])
        dataframe = pd.read_csv(StringIO(block))
        transfers = []
        for row in dataframe.to_dict(orient="records"):
            source_plate = plates_dict[row["Source Plate Name"]]
            source_well = source_plate.wells[row.pop("Source Well")]
            dest_plate = plates_dict[row["Destination Plate Name"]]
            dest_well = dest_plate.wells[row.pop("Destination Well")]
            volume = float(row.pop("Actual Volume"))
            transfers.append(Transfer(
                volume=(1e-9)*volume,
                source_well=source_well,
                destination_well=dest_well,
                metadata=row
            ))

        return transfers

    def add_plates_from_metadata(metadata, plates_dict):
        for role in ("Source", "Destination"):
            source_plate = metadata["%s Plate Name" % role]
            if source_plate not in plates_dict:
                plate_type = metadata["%s Plate Type" % role]
                if "1536" in plate_type:
                    num_wells = 1536
                elif "384" in plate_type:
                    num_wells = 384
                else:
                    num_wells = 96
                plates_dict[source_plate] = Plate(
                    num_wells=num_wells,
                    name=source_plate,
                    metadata={
                        "plate_barcode": metadata["%s Plate Barcode" % role],
                        "plate_type": plate_type,
                    }
                )

    blocks = [
        block
        for block in filecontent.split("\r\n\r\n")
        if block != ""
    ]

    picklist_metadata = {"filename": filename}
    for block in blocks:

        if block.startswith("Run ID"):
            read_key_value_block(block, target_dict=picklist_metadata)

        if block.startswith("[EXCEPTIONS]"):
            transfers_exceptions_list = block_to_transfers_list(block)
        else:
            transfers_exceptions_list = []

        if block.startswith("[DETAILS]"):
            transfers_list = block_to_transfers_list(block)

        if block.startswith("Instrument Name"):
            read_key_value_block(block, target_dict=picklist_metadata)

    all_transfers = transfers_list + transfers_exceptions_list

    for transfer in all_transfers:
        add_plates_from_metadata(transfer.metadata, plates_dict)
    for transfer in all_transfers:
        meta = transfer.metadata
        transfer.source_plate = plates_dict[meta["Source Plate Name"]]
        transfer.destination_plate = plates_dict[
            meta["Destination Plate Name"]]
        obsolete_fields = [
            field for field in meta
            if any(e in field for e in ("Plate Name", "Plate Type",
                                        "Plate Barcode"))
        ]
        for field in obsolete_fields:
            meta.pop(field)

    picklist_metadata["exceptions"] = PickList(transfers_exceptions_list)
    picklist_metadata["plates_dict"] = plates_dict

    return PickList(
        transfers_list=transfers_list,
        metadata=picklist_metadata
    )
