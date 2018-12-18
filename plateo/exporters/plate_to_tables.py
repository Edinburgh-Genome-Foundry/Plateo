from collections import defaultdict
from ..tools import number_to_rowname, unit_factors
import pandas

def plate_to_platemap_spreadsheet(plate, wellinfo_function, filepath=None,
                                  sheet_name='plate_map', headers=True):
    """Generate a spreadsheet with a map of the plate.

    Parameters
    ----------

    plate
      A Plate object

    filepath
      Path to a ".csv" or ".xls(x)" file. Or a Pandas ExcelWriter object.

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
    elif str(filepath).lower().endswith(".csv"):
        dataframe.to_csv(filepath, header=headers, index=headers)
    else:
        dataframe.to_excel(filepath, sheet_name=sheet_name, header=headers,
                           index=headers)

def plate_to_pandas_dataframe(plate, fields=None, direction='row'):
    """Return a dataframe with the info on each well"""
    dataframe = pandas.DataFrame.from_records(plate.to_dict()["wells"]).T
    by = (["row", "column"] if direction == 'row' else ['column', 'row'])
    dataframe = dataframe.sort_values(by=by)
    if fields is not None:
        dataframe = dataframe[fields]
    return dataframe

def plate_to_content_spreadsheet(plate, filepath, content_type=None,
                                 volume_unit='uL',
                                 concentration_unit='ng-uL'):
    """Write plate into Excel with 'content', 'volume', 'concentration' sheets.

    The 'content' sheet will contain a platemap of the product contained in
    each well (e.g. a part name or a strain name)

    The 'volume' sheet will contain a platemap of the volume contained in each
    well (e.g. a part name or a strain name) in liter

    The 'concentration' sheet will contain a platemap of the concentration
    contained in each well (e.g. a part name or a strain name) in gram/liter.


    Parameters
    ----------
    plate
      Plate to be written. The content of each well must have a single product.

    filepath
      Path to the excel spreadsheet to write. An Excel writer also works.
    """

    volume_factor = unit_factors[volume_unit]
    c_mass, c_vol = concentration_unit.split('-')
    concentration_factor = unit_factors[c_mass] / unit_factors[c_vol]

    functions = [
        (('content (%s)' % content_type) if content_type else 'content',
         lambda w: w.content.components_as_string()),
        ('volume (%s)' % volume_unit,
        lambda w: w.content.volume / volume_factor),
        ('concentration (%s)' % concentration_unit,
        lambda w: w.content.concentration() / concentration_factor)
    ]
    writer = pandas.ExcelWriter(filepath)
    for name, fun in functions:
        plate_to_platemap_spreadsheet(plate, fun, sheet_name=name,
                                      filepath=writer)
    writer.close()
