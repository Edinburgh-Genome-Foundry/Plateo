import zipfile
import sys
PYTHON3 = (sys.version_info[0] == 3)

if PYTHON3:
    from io import StringIO
else:
    from StringIO import StringIO

import pandas
import matplotlib.image as mpimg
import numpy as np
from ..containers import Plate96

def plate_from_aati_fragment_analyzer_peaktable(filename):
    """"Return a Plate96 object with a data field for the ``bands``.

    Provided a ``filename`` of an AATI fragment analyzer Peak table
    (these are generally named ``{DATE} Peak Table.csv``), it generates a
    Plate96 object where each well has a data attribute "bands" of the form
    ``{peak_id: {attrs}}`` where the ``peak_id`` is a number (>1) and the attrs
    attribute has fields such as ``Size (bp)``, ``% (Conc.)``, ``nmole/L``,
    ``ng/ul``, ``RFU``.

    """
    df = pandas.read_csv(filename)
    wells = {
        name: {"bands": {
            peak_id: row.to_dict()
            for peak_id, row in d.set_index("Peak ID").iterrows()
            if row["% (Conc.)"] > 0
        }}
        for name, d in df.groupby(["Well"])
    }
    return Plate96(wells_data=wells)

def plate_from_aati_fa_gel_image(filename):
    """Return a Plate96 where each well stores an image of the gel migration

    Each well has a ``data["migration_image"]`` which is a WxH
    array, a greyscale version of the image.
    """
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
        well.data["migration_image"] = img[ymin:ymax, x1:x2]
    return plate


def plate_from_aati_fragment_analyzer_zip(filename):
    """"Return a Plate96 object with data for bands and migration image.

    Provided a zip output of an AATI fragment analyzer, it will find the
    relevant files and extract band sizes and gel images, and store these in
    each well's data.

    In the final plate, each well has a data attribute "bands" of the form
    ``{peak_id: {attrs}}`` where the ``peak_id`` is a number (>1) and the attrs
    attribute has fields such as ``Size (bp)``, ``% (Conc.)``, ``nmole/L``,
    ``ng/ul``, ``RFU``.

    Each well also has a  ``data["migration_image"]`` which is a WxH
    array, a greyscale version of the image.
    """
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
    plate.data["ladder"] = ladder
    if images_plate is not None:
        plate.merge_data_from(images_plate)
    return plate
