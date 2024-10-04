from plateo.parsers import plate_from_content_spreadsheet
from plateo.applications.doe import (
    import_valuetable_from_csv,
    convert_valuetable_to_volumetable,
    convert_volumetable_to_actiontable,
)
from plateo.containers import Plate96
from plateo.parsers.picklist_from_tables import picklist_from_dataframe
from plateo.exporters import (
    picklist_to_tecan_evo_picklist_file,
    plate_to_content_spreadsheet,
    plate_to_platemap_spreadsheet,
)

# READ THE SOURCE PLATE FROM A CONTENT SPREADSHEET
source_plate = plate_from_content_spreadsheet("Source_Plate.xlsx")
source_plate.name = "source"

# IMPORT THE TABLE SPECIFYING THE DESIRED FACTOR LEVELS FOR EACH EXPERIMENTAL UNIT
valuetable = import_valuetable_from_csv("valuetable.csv")
valuetable.head()

# CONVERT TO A TABLE SPECIFYING THE DESIRED VOLUMES FOR EACH FACTOR
volumetable = convert_valuetable_to_volumetable(valuetable, source_plate)
volumetable.head()

# FOR THE NEXT STEP WE NEED A DESTINATION PLATE
dest_plate = Plate96(name="dest")

# AT THIS STEP WE ARRIVE AT THE IMPLEMENTATION STAGE
actiontable = convert_volumetable_to_actiontable(volumetable, source_plate, dest_plate)
actiontable.head()

# CREATE PICKLIST THEN EXPORT IT AS A TECAN (GEMINI) WORKLIST
picklist = picklist_from_dataframe(
    dataframe=actiontable,
    source_plates=[source_plate],
    dest_plates=[dest_plate],
    df_columns=None,
)
picklist_to_tecan_evo_picklist_file(picklist, "out_tecan_picklist.gwl")

# SIMULATE THE PICKLIST
simulated_plates = picklist.simulate(inplace=False)
simulated_final_plate = simulated_plates[dest_plate]

# EXPORT THE SIMULATED FINAL PLATE AS AN EXCEL SPREADSHEET
plate_to_content_spreadsheet(simulated_final_plate, "out_final_plate.xlsx")
# This records the contents, rather than the experimental units, for each well.


# EXPORT A PLATEMAP OF EXPERIMENTAL UNITS
def info_function(well):
    if "expunit" in well.data:
        return well.data["expunit"]
    else:
        return None


plate_to_platemap_spreadsheet(
    dest_plate,
    wellinfo_function=info_function,
    filepath="out_final_plate_expunits.xlsx",
)
