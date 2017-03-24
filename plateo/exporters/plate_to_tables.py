from collections import defaultdict
from ..tools import number_to_rowname
import pandas

def plate_to_platemap_spreadsheet(plate, wellinfo_function, filepath=None):
    """Generate a spreadsheet with a map of the plate.

    Parameters
    ----------

    plate
      A Plate object

    filepath
      Path to a ".csv" or ".xls(x)" file

    wellinfo_function
      A function `f(well) -> info` where `well` is a Well object of the
      plate and the returned `info` is an information about the well that
      will be displayed in the well's cell in the final spreadsheet. The
      info can be a string or any other object that can be converted to a
      string

      .. code:: bash

             1  2  3  4  5  6  7  8  9  10 11 12
          A  .  .  .  .  .  .  .  .  .  .  .  .
          B  .  .  .  .  .  .  .  .  .  .  .  .
          C  .  .  .  .  .  .  .  .  .  .  .  .
          D  .  .  .  .  .  .  .  .  .  .  .  .
          E  .  .  .  .  .  .  .  .  .  .  .  .
          F  .  .  .  .  .  .  .  .  .  .  .  .
          G  .  .  .  .  .  .  .  .  .  .  .  .
          H  .  .  .  .  .  .  .  .  .  .  .  .

        """

    platedict = defaultdict(lambda *a: {})
    for well in plate:
        info = wellinfo_function(well)
        platedict[well.column][number_to_rowname(well.row)] = info
    dataframe = pandas.DataFrame.from_dict(platedict)
    if filepath is None:
        return dataframe
    elif filepath.lower().endswith(".csv"):
        dataframe.to_csv(filepath)
    else:
        dataframe.to_excel(filepath)

def plate_to_pandas_dataframe(plate, fields=None, direction='row'):
    """Return a dataframe with the info on each well"""
    dataframe = pandas.DataFrame.from_records(plate.to_dict()["wells"]).T
    by = (["row", "column"] if direction == 'row' else ['column', 'row'])
    dataframe = dataframe.sort_values(by=by)
    if fields is not None:
        dataframe = dataframe[fields]
    return dataframe
