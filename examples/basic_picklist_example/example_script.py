from plateo import PickList
from plateo.containers import Plate96
from plateo.parsers.plate_from_tables import plate_from_content_spreadsheet
from plateo.exporters import picklist_to_labcyte_echo_picklist_file
from plateo.exporters import PlateTextPlotter, plate_to_content_spreadsheet

# READ THE SOURCE PLATE FROM A CONTENT SPREADSHEET

source_plate = plate_from_content_spreadsheet("example_echo_plate.xlsx")
source_plate.name = "Source"
destination_plate = Plate96(name="Destination")


# CREATE A PICKLIST AND ADD A FEW TRANSFERS IN IT
picklist = PickList()

picklist.add_transfer(
    source_well=source_plate.wells["A1"],
    destination_well=destination_plate.wells["A5"],
    volume=100e-9,  # 100 nanoliter
)

picklist.add_transfer(
    source_well=source_plate.wells["C5"],
    destination_well=destination_plate.wells["A5"],
    volume=100e-9,  # 100 nanoliter
)

picklist.add_transfer(
    source_well=source_plate.wells["D6"],
    destination_well=destination_plate.wells["B1"],
    volume=100e-9,  # 100 nanoliter
)

# EXPORT PICKLIST AS ECHO PICKLIST

picklist_to_labcyte_echo_picklist_file(picklist, "my_picklist.csv")


# SIMULATE THE PICKLIST
# This will catch errors such as pipetting from an empty well, etc.

simulated_plates = picklist.simulate(inplace=False)
simulated_final_plate = simulated_plates[destination_plate]

# EXPORT THE SIMULATED FINAL PLATE AS AN EXCEL SPREADSHEET FOR EYEBALLING

plate_to_content_spreadsheet(simulated_final_plate, "my_final_plate.xlsx")


# EXPORT THE SIMULATED FINAL PLATE AS A PDF FIGURE


def reagents_in_well(well):
    return well.content.components_as_string(separator="\n")


plotter = PlateTextPlotter(reagents_in_well)
ax, stats = plotter.plot_plate(simulated_final_plate, figsize=(20, 10))
ax.figure.savefig("my_final_plate.pdf")
