from ..PlateLayout import PlateLayout
import pandas as pd


def plate_from_dataframe(dataframe, wellname_field="wellname", num_wells=96,
                         metadata=None):
    dataframe = dataframe.set_index(wellname_field)
    wells_metadata = {
        well: row.to_dict()
        for well, row in dataframe.iterrows()
    }
    return PlateLayout(
        num_wells=num_wells,
        wells_metadata=wells_metadata,
        metadata=metadata
    )


def plate_from_list_spreadsheet(filename, sheetname=0, num_wells=96,
                                wellname_field="wellname"):

    if ".xls" in filename:  # includes xlsx
        dataframe = pd.read_excel(filename, sheetname=sheetname)
    elif filename.endswith(".csv"):
        dataframe = pd.read_csv(filename)
    return plate_from_dataframe(dataframe, wellname_field=wellname_field,
                                num_wells=num_wells,
                                metadata={"filename": filename})
