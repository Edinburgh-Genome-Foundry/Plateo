import re
import os

import pandas as pd

from plateo.containers import get_plate_class
from ..tools import (infer_plate_size_from_wellnames, number_to_rowname,
                     unit_factors)

def plate_from_dataframe(dataframe, wellname_field="wellname",
                         num_wells="infer", data=None):
    """Create a plate from a Pandas dataframe where each row contains the
    name of a well and data on the well.

    it is assumed that the dataframe's index is given by the well names.

    This function is used e.g. in `plate_from_list_spreadsheet`.

    Parameters
    ----------

    dataframe
      A Pandas dataframe

    wellname_field
      The name of the Pandas dataframe column indicating the name of the wells.

    num_wells
      Number of wells in the Plate to be created. If left to default 'infer',
      the size of the plate will be chosen as the smallest format (out of
      96, 384 and 1536 wells) which contains all the well names.

    data
      Metadata information for the plate.
    """

    # TODO: infer plate class automatically ?

    dataframe = dataframe.set_index(wellname_field)
    wells_data = {
        well: row.to_dict()
        for well, row in dataframe.iterrows()
    }
    if num_wells == "infer":
        num_wells = infer_plate_size_from_wellnames(wells_data.keys())
    plate_class = get_plate_class(num_wells=num_wells)
    return plate_class(wells_data=wells_data, data=data)


def plate_from_list_spreadsheet(filename, sheet_name=0, num_wells="infer",
                                wellname_field="wellname"):
    """Create a plate from a Pandas dataframe where each row contains the
    name of a well and metadata on the well.


    Parameters
    ----------

    filename
      Path to the spreadsheet file.

    sheet_name
      Index or name of the spreadsheet to use.

    num_wells
      Number of wells in the Plate to be created. If left to default 'infer',
      the size of the plate will be chosen as the smallest format (out of
      96, 384 and 1536 wells) which contains all the well names.

    wellname_field="wellname"
      Name of the column of the spreadsheet giving the well names
    """

    if ".xls" in filename:  # includes xlsx
        dataframe = pd.read_excel(filename, sheet_name=sheet_name)
    elif filename.endswith(".csv"):
        dataframe = pd.read_csv(filename)
    return plate_from_dataframe(dataframe, wellname_field=wellname_field,
                                num_wells=num_wells,
                                data={"filename": filename})


def plate_from_platemap_spreadsheet(file_handle, file_type="auto",
                                    original_filename=None, data_field="info",
                                    num_wells="infer", plate_class=None,
                                    multiply_by=None,
                                    headers=True, sheet_name=0, skiprows=None):
    """Parse spreadsheets representing a plate map.

    Parameters
    ----------

    file_handle
      Either a file handle or a file path to a CSV/Excel spreadsheet. If a file
      handle is provided, then the file_type must be set, or at least the
      "original_filename".

    file_type
      Either "csv" or "excel" or "auto" (at which case the type is determined
      based on the provided file path in ``file_handle`` or
      ``original_filename``)

    original_filename
      Original filename (optional if file_handle is already a file path or
      if file_type is specified)

    data_field
      Data field of the well under which platemap's information will be stored

    num_wells
      Number of wells in the Plate to be created. If left to default 'infer',
      the size of the plate will be chosen as the smallest format (out of
      96, 384 and 1536 wells) which contains all the well names.

    headers
      Whether the spreadsheet actually writes the "A" "B", and "1" "2"


    skiprows
      Number of rows to skip (= rows before the platemap starts)

    The spreadsheet should be either a 8 rows x 12 columns csv/excel file,
    or have headers like this

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
    if isinstance(file_handle, str):
        # The provided file is a file path
        original_filename = file_handle

    if file_type == "auto":
        # Determine the file type based on the file name.
        base, ext = os.path.splitext(original_filename)
        ext = ext.lower()
        if ext == ".csv":
            file_type = "csv"
        elif ext in [".xls", ".xlsx"]:
            file_type = "excel"

    index_col = 0 if headers else None
    if file_type == "csv":
        dataframe = pd.read_csv(file_handle, index_col=index_col,
                                header=index_col, skiprows=skiprows)
    elif file_type == "excel":
        dataframe = pd.read_excel(file_handle, index_col=index_col,
                                  sheet_name=sheet_name,
                                  header=index_col, skiprows=skiprows)
    if headers:
        wells_data = {
            row + str(column): {
                data_field: content if (multiply_by is None) else
                            content * multiply_by
            }
            for column, column_content in dataframe.to_dict().items()
            for row, content in column_content.items()
        }
    else:
        wells_data = {
            number_to_rowname(row + 1) + str(column + 1):
                {data_field: content}
            for column, column_content in dataframe.to_dict().items()
            for row, content in column_content.items()
        }
    if num_wells == "infer":
        num_wells = infer_plate_size_from_wellnames(wells_data.keys())
    if plate_class is None:
        plate_class = get_plate_class(num_wells=num_wells)
    return plate_class(wells_data=wells_data,
                       data={"file_source": original_filename})


def plate_from_content_spreadsheet(filepath, headers=True, plate_class=None,
                                   sheet_names='default'):
    """Load plate from Excel with 'content', 'volume', 'concentration' sheets.

    The 'content' sheet contains a platemap of the product contained in each
    well (e.g. a part name or a strain name)

    The 'volume' sheet contains a platemap of the volume contained in each
    well (e.g. a part name or a strain name) in liter

    The 'concentration' sheet contains a platemap of the concentration
    contained in each well (e.g. a part name or a strain name) in gram/liter.


    Parameters
    ----------
    filepath
      Path to the excel spreadsheet

    headers
      Set to True if the spreadsheets represent the platemaps using headers
      ABCDEF... for columns and 123456... for rows

    plate_class
      Class of the plate returned. If set to None, a generic Plate96 or
      Plate384 or other is returned depending on the autodetected plate size

    sheet_name
      A triple of the name of the sheets containing
    """

    sheet_names = pd.ExcelFile(filepath).sheet_names

    sheet_name_patterns = {
        'concentration': r"[cC]oncentration(| \((\S+)-(\S+)\))",
        'volume': r"[vV]olume(| \((\S+)\))",
        'content': r"[cC]ontent(| \((\S+)\))"
    }

    default_factors = {
        'concentration': 1e-3, # default is ng/ul = 0.001 g/l
        'volume': 1e-6, # default is ul
        'content': 'content'
    }

    field_data = {}
    for field, pattern in sheet_name_patterns.items():
        for sheet_name in sheet_names:
            match = re.fullmatch(pattern, sheet_name)
            if match is not None:
                field_data[field] = data = {'sheet_name': sheet_name}
                groups = list(match.groups())
                if groups[0] == '':
                    data['factor'] = default_factors[field]
                elif len(groups) == 2:
                    if field == 'content':
                        data['factor'] = groups[1]
                    else:
                        data['factor'] = unit_factors[groups[1]]
                elif len(groups) == 3:
                    factor = unit_factors[groups[1]] / unit_factors[groups[2]]
                    data['factor'] = factor
                else:
                    raise ValueError("Couldn't parse sheet %s" % sheet_name)
                break
        else:
            raise ValueError(("No sheet found for field %s."
                              "Check your sheet names." % sheet_name))

    content_field_name = field_data['content']['factor']
    plate = plate_from_platemap_spreadsheet(
        filepath,  headers=headers, original_filename=filepath,
        sheet_name=field_data['content']['sheet_name'],
        data_field=content_field_name,
        plate_class=plate_class    
    )
    plate.merge_data_from(
        plate_from_platemap_spreadsheet(
            filepath, data_field='volume',
            headers=headers, original_filename=filepath,
            multiply_by=field_data['volume']['factor'],
            sheet_name=field_data['volume']['sheet_name']
        )
    )
    plate.merge_data_from(
        plate_from_platemap_spreadsheet(
            filepath, data_field='concentration', headers=headers,
            sheet_name=field_data['concentration']['sheet_name'],
            multiply_by=field_data['concentration']['factor'],
            original_filename='x.xlsx'
        )
    )

    for well in plate.iter_wells():
        content = well.data[content_field_name]
        if str(content) == 'nan':
            well.data[content_field_name] = None
            continue
        volume = well.data.volume
        concentration = well.data.concentration

        try:
            well.add_content({content: volume * concentration}, volume=volume)
        except Exception as err:
            raise type(err)("Check your data for well %s" % well.name) from err
        for field in ('volume', 'concentration'):
            well.data.pop(field)

    return plate
