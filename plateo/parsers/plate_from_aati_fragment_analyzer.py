import zipfile
from StringIO import StringIO
import pandas
import matplotlib.image as mpimg
import numpy as np
from ..containers import Plate96

def plate_from_aati_fragment_analyzer_peaktable(filename):
    df = pandas.read_csv(filename)
    wells = {
        name: {"bands": {
            peak_id: row.to_dict()
            for peak_id, row in d.set_index("Peak ID").iterrows()
            if row["% (Conc.)"] > 0
        }}
        for name, d in df.groupby(["Well"])
    }
    return Plate96(wells_metadata=wells)

def plate_from_aati_fa_gel_image(filename):
    img = mpimg.imread(filename)
    black_white = img.mean(axis=2)
    threshold = black_white > 0.9
    vertical_lines = (threshold.sum(axis=0) < 200).nonzero()[0]
    xmin, xmax = vertical_lines.min() + 1, vertical_lines.max() - 1
    horizontal_lines = (threshold.sum(axis=1) < 200).nonzero()[0]
    ymin, ymax = horizontal_lines.min() + 1, horizontal_lines.max() - 1
    xx = np.linspace(xmin, xmax, 97).round(0).astype(int)
    plate = Plate96("Gel Image")
    wells = plate.iter_wells(direction="column")
    bands_x = zip(xx, xx[1:])
    for (x1, x2), well in zip(bands_x, wells):
        well.metadata["migration_image"] = img[ymin:ymax, x1:x2]
    return plate


def plate_from_aati_fragment_analyzer_zip(filename):
    ladder = None
    images_plate = None
    with zipfile.ZipFile(filename) as f:
        for name in f.namelist():
            if name.endswith('Peak Table.csv'):
                content = StringIO(f.read(name))
                plate = plate_from_aati_fragment_analyzer_peaktable(content)
            if name.endswith('Size Calibration.csv'):
                ladder = pandas.read_csv(StringIO(f.read(name)))
            if name.endswith('Gel.PNG'):
                content = StringIO(f.read(name))
                images_plate = plate_from_aati_fa_gel_image(content)
    plate.metadata["ladder"] = ladder
    if images_plate is not None:
        plate.merge_metadata_from(images_plate)
    return plate


#
# def parse_fragment_analyzer_peaktable(filename):
#     # legacy, old format
#
#     def _find_fa_output_blocks(filename):
#         with open(filename, "r") as f:
#             lines = [line.strip().split(",") for line in f.readlines()]
#         blocs_beginnings = [0] + [
#             i
#             for i in range(2, len(lines))
#             if (lines[i - 1][0] == '') and (lines[i][0] != '')
#         ] + [len(lines)]
#         blocks = [
#             lines[a:b]
#             for a, b in zip(blocs_beginnings, blocs_beginnings[1:])
#         ]
#         return blocks
#
#
#     def _treat_fa_output_block(lines):
#         block = {
#             "well_name": lines[0][0].strip(":"),
#             "label": lines[0][1],
#             "peaks": {},
#             "attributes": {}
#         }
#         labels = ("id", "size", "%concentration", "nmole/L", "ng/ul", "RFU")
#         for line in lines[2:]:
#             if line[0] != '':
#                 peak = dict(zip(labels, line))
#                 if " " in peak["size"]:
#                     peak["size"], peak["label"] = peak["size"].split()
#                 else:
#                     peak["label"] = ""
#                 if peak["%concentration"] == '':
#                     peak["%concentration"] = 0
#
#                 types = {
#                     "id": int,
#                     "size": int,
#                     "%concentration": float,
#                     "nmole/L": float,
#                     "ng/ul": float,
#                     "RFU": int
#                 }
#                 for field, ftype in types.items():
#                     peak[field] = ftype(peak[field])
#                 block["peaks"][peak["id"]] = peak
#
#             if line[1].startswith(("TIM", "TIC", "Total Conc.")):
#                 field, quantity, unit = line[1][:-1], float(line[2]), line[3]
#                 block["attributes"][field] = {
#                     "field": field,
#                     "quantity": quantity,
#                     "unit": unit
#                 }
#         return block
#
#     blocks = [
#         _treat_fa_output_block(block)
#         for block in _find_fa_output_blocks(filename)
#     ]
#
#     return {
#         block["well_name"]: block
#         for block in blocks
#     }
