import pandas

from plateo.tools import index_to_wellname
from plateo.parsers.file_parsers import parse_excel_xml
from plateo.parsers.plate_from_tables import plate_from_dataframe
from plateo import Plate

def plate_from_nanodrop_xml_file(xml_file, num_wells=96, direction="row"):
    """Return a plate with the DNa concentrations measured by the Nanodrop.

    Parameters
    ----------

    xml_file
    


    Returns
    -------

    A Plate where the wells have the following metadata fields.

    """
    table = parse_excel_xml(xml_file)[0]
    dataframe = pandas.DataFrame(table[1:], columns=table[0])
    for column in dataframe.columns:
        dataframe[column] = pandas.to_numeric(dataframe[column],
                                              errors='ignore')

    def wellname(i):
        return index_to_wellname(int(i), num_wells, direction=direction)
    dataframe["wellname"] = dataframe["#"].apply(wellname)
    return plate_from_dataframe(dataframe)
