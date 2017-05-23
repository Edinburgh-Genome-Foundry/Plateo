import pandas

from plateo.tools import index_to_wellname
from plateo.parsers.file_parsers import parse_excel_xml
from plateo.parsers.plate_from_tables import plate_from_dataframe
import numpy as np


def parse_numeric(numeric_wannabe):
    try:
        return float(numeric_wannabe)
    except ValueError:
        return np.nan

def plate_from_nanodrop_xml_file(xml_file=None, xml_string=None, num_wells=96,
                                 direction="row"):
    """Return a plate with the DNA concentrations measured by the Nanodrop.

    Parameters
    ----------

    xml_file
      The xml file exported from the Nanodrop software. It should contain one
      measurement per well. An xml_string can be provided instead of this
      argument.

    xml_string
       The content of an xml file exported from the Nanodrop software. Can be
       provided instead of xml_file. Should contain one measurement per well.

    num_wells
      Number of wells in the Plate

    direction
      Either ``row`` or `column``. Order of the measurements on the plate.


    Returns
    -------

    A Plate where the wells have the following data fields:
    TODO: complete

    """

    table = parse_excel_xml(xml_file=xml_file, xml_string=xml_string)[0]
    dataframe = pandas.DataFrame(table[1:], columns=table[0])
    for column in dataframe.columns:
        dataframe[column] = pandas.to_numeric(dataframe[column],
                                              errors='ignore')

    def wellname(i):
        return index_to_wellname(int(i), num_wells, direction=direction)
    dataframe["wellname"] = dataframe["#"].apply(wellname)
    dataframe["Nucleic Acid"] = [parse_numeric(e)
                                 for e in dataframe["Nucleic Acid"]]
    return plate_from_dataframe(dataframe)
