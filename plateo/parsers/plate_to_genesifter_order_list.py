import pandas

def plate_to_genesift_ordering_spreadsheet(plate, filename, label_fun,
                                           direction="row"):
    """Generate a spreadsheet for ordering with genesift sequencing ordering
    systems. the spreadsheet has two columns: Position (in the plate)
    and Sample (a label).

    Parameters
    ----------

    plate
      A plate

    filename
      Output file name for the excel file e.g. myorder.xls

    label_fun
      A function well-> label. Return None for wells you want to ignore.

    direction
      Direction in which the wells are considered.

    """
    pandas.DataFrame.from_records([
        {
            "Position": i+1,
            "Sample": label_fun(well)
        }
        for i, well in enumerate(plate.iter_wells(direction="column"))
        if label_fun(well) is not None
    ]).to_excel(filename, index=False, columns=["Position", "Sample"])
