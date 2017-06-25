from ..containers import Plate96
import pandas

def plate_from_nanoquant_reads(nanoquant_files, plate_class=Plate96,
                               direction="column"):
    """Return a plate of DNA concentrations and qualities from NanoQuant reads.

    Parameters
    ----------

    nanoquant_files
      List of file paths or file-like objects, pointing each to a nanoquant
      read (which is a simple table of 16 concentration-quality pairs).

    plate_class
      The plateo container class of the plate to return, e.g. Plate96, or
      Plate384

    direction
      either row or column depending on which directions the wells of the
      original plates were sampled. But due to the shape of the nanoquant,
      it will certainly always be column.

    Returns
    -------

    A plate object where wells have attributes ``well.data.concentration``
    (in microg / microL) and a ``well.data.quality`` (log ratio 220 / 230).
    """
    plate = plate_class()
    wells = plate.iter_wells(direction=direction)
    for nanoquant_file in nanoquant_files:
        dataframe = pandas.read_excel(nanoquant_file, header=None)
        for i, row in dataframe.iterrows():
            well = next(wells)
            well.data["concentration"] = row[0]
            well.data["concentration_unit"] = "microg / microL"
            well.data["quality"] = row[1]
            well.data["quality_label"] = "log ratio 220/230"
    return plate
