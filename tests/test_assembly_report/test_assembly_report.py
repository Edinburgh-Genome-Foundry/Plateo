import os

import matplotlib

matplotlib.use("Agg")

from plateo import AssemblyPlan
from plateo.parsers import plate_from_content_spreadsheet
from plateo.containers.plates import Plate4ti0960
from plateo.exporters import (
    picklist_to_labcyte_echo_picklist_file,
    PlateTextPlotter,
    AssemblyPicklistGenerator,
    picklist_to_assembly_mix_report,
)
from plateo.tools import human_volume
import flametree
from pandas import pandas
from collections import OrderedDict
import matplotlib.pyplot as plt
from Bio import SeqIO


def test_assembly_report(tmpdir):
    data_path = os.path.join("tests", "test_assembly_report", "data")
    root = flametree.file_tree(data_path)
    df = pandas.read_excel(
        root.example_picklist_xls.open("rb"), index_col=0, engine="xlrd"
    )
    assembly_plan = AssemblyPlan(
        OrderedDict(
            [
                (row[0], [e for e in row[1:] if str(e) not in ["-", "nan"]])
                for i, row in df.iterrows()
                if row[0] not in ["nan", "Construct name"]
            ]
        )
    )
    parts_zip = flametree.file_tree(root.emma_parts_zip._path)

    def read(f):
        record = SeqIO.read(f.open("r"), "genbank")
        record.id = f._name_no_extension
        return record

    parts_data = {
        f._name_no_extension: {"record": read(f)}
        for f in parts_zip._all_files
        if f._extension == "gb"
    }
    assembly_plan.parts_data = parts_data
    source_plate = plate_from_content_spreadsheet(root.example_echo_plate_xlsx._path)

    source_plate.name = "Source"
    for well in source_plate.iter_wells():
        if not well.is_empty:
            content = well.content.components_as_string()

    destination_plate = Plate4ti0960("Mixplate")

    picklist_generator = AssemblyPicklistGenerator(
        part_mol=1.3e-15,
        complement_to=1e-6,
        buffer_volume=300e-9,
        volume_rounding=2.5e-9,
        minimal_dispense_volume=5e-9,
    )
    picklist, data = picklist_generator.make_picklist(
        assembly_plan,
        source_wells=source_plate.iter_wells(),
        destination_wells=destination_plate.iter_wells(direction="column"),
        complement_well=source_plate.wells.O24,
        buffer_well=source_plate.wells.P24,
    )
    future_plates = picklist.execute(inplace=False)

    def text(w):
        txt = human_volume(w.content.volume)
        if "construct" in w.data:
            txt = "\n".join([w.data.construct, txt])
        return txt

    plotter = PlateTextPlotter(text)
    ax, _ = plotter.plot_plate(future_plates[destination_plate], figsize=(20, 8))

    ziproot = flametree.file_tree(os.path.join(str(tmpdir), "a.zip"))
    ax.figure.savefig(
        ziproot._file("final_mixplate.pdf").open("wb"),
        format="pdf",
        bbox_inches="tight",
    )
    plt.close(ax.figure)
    picklist_to_assembly_mix_report(
        picklist,
        ziproot._file("assembly_mix_picklist_report.pdf").open("wb"),
        data=data,
    )
    assembly_plan.write_report(ziproot._file("assembly_plan_summary.pdf").open("wb"))
    picklist_to_labcyte_echo_picklist_file(
        picklist, ziproot._file("ECHO_picklist.csv").open("w")
    )
    ziproot._close()
