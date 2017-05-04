from ..PickList import PickList, Transfer
from ..Plate import Plate
from ..containers import Plate96, Plate384, Plate1536
import pandas as pd
import sys
PYTHON3 = (sys.version_info[0] == 3)

if PYTHON3:
    from io import StringIO
else:
    from StringIO import StringIO

def picklist_from_labcyte_echo_logfile(logfile=None, logcontent=None,
                                       plates_dict=None):
    """Return a picklist of what was actually dispensed in the ECHO, based
    on the log file.

    Picklist.metadata["exceptions"] is a picklist of all transfers that went
    wrong.

    Parameters
    ----------

    logfile
      The path to the echo logfile.

    logcontent
      Echo logfile content, can be provided instead of filename

    plates_dict
      A dictionary of the form {'Plate name': Plate()} linking the plate names
      found in the Echo logs to Plateo Plate objects. If None is provided,
      plates are infered from the Echo logs (a bit experimental).

    """

    if plates_dict is None:
        plates_dict = {}

    if logfile is not None:
        with open(logfile) as f:
            logcontent = f.read()

    def read_key_value_block(block, target_dict):
        """Read a block of line of the form 'key, value\nkey, value\n...'"""
        for line in block.splitlines():
            key, value = line.split(",")
            target_dict[key] = value

    def block_to_transfers_list(block):
        """Return a list of transfers from the block of lines."""
        block = "\n".join(block.splitlines()[1:])
        dataframe = pd.read_csv(StringIO(block))
        transfers = []

        for i, row in dataframe.iterrows():
            for role in ("Source", "Destination"):
                plate = row["%s Plate Name" % role]
                if plate not in plates_dict:
                    plate_type = row["%s Plate Type" % role]
                    if "1536" in plate_type:
                        plate_class = Plate1536
                    elif "384" in plate_type:
                        plate_class = Plate384
                    else:
                        plate_class = Plate96
                    plates_dict[plate] = plate_class(
                        name=plate,
                        data={
                            "plate_barcode": row["%s Plate Barcode" % role],
                            "plate_type": plate_type,
                        }
                    )

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
                data=row
            ))

        return transfers

    def add_plates_from_metadata(metadata, plates_dict):
        """Auto-find plates in the log file"""
        for role in ("Source", "Destination"):
            plate = metadata["%s Plate Name" % role]
            if plate not in plates_dict:
                plate_type = metadata["%s Plate Type" % role]
                if "1536" in plate_type:
                    num_wells = 1536
                elif "384" in plate_type:
                    num_wells = 384
                else:
                    num_wells = 96
                plates_dict[plate] = Plate(
                    num_wells=num_wells,
                    name=plate,
                    data={
                        "plate_barcode": metadata["%s Plate Barcode" % role],
                        "plate_type": plate_type,
                    }
                )

    blocks = [
        block
        for block in logcontent.split("\r\n\r\n")
        if block != ""
    ]

    picklist_metadata = {"logfile": logfile}
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
        add_plates_from_metadata(transfer.data, plates_dict)
    for transfer in all_transfers:
        meta = transfer.data
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
        data=picklist_metadata
    )
