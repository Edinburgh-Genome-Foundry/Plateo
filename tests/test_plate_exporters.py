from plateo.exporters import (plate_to_platemap_spreadsheet,
                              plate_to_genesift_sequencing_order_spreadsheet,
                              plate_to_pandas_dataframe,
                              plate_to_bokeh_plot,
                              PlateTextPlotter,
                              PlateGraphsPlotter,
                              PlateColorsPlotter)
from plateo.containers import Plate96

def test_plate_to_platemap_spreadsheet():
    plate = Plate96("TestPlate")


def test_plate_to_genesift_sequencing_order_spreadsheet():
    plate_to_genesift_sequencing_order_spreadsheet


def test_plate_to_pandas_dataframe():
    plate_to_pandas_dataframe


def test_plate_to_bokeh_plot():
    plate_to_bokeh_plot


def test_PlateTextPlotter():
    PlateTextPlotter


def test_PlateGraphsPlotter():
    PlateGraphsPlotter


def test_PlateColorsPlotter():
    PlateColorsPlotter
