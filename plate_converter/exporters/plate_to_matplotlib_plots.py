import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.axes_grid.inset_locator import inset_axes

import numpy as np
from tqdm import tqdm

from ..tools import (
    compute_rows_columns,
    wellname_to_coordinates,
    number_to_rowname
)

letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def draw_plate_layout(num_wells, ax):
    n_rows, n_columns = compute_rows_columns(num_wells)
    ax.axis("off")
    ax.add_patch(patches.Rectangle((0.5, 0.5), n_columns, n_rows, fill=False))
    for i in range(1, n_columns + 1):
        ax.text(i, 8.6, str(i), horizontalalignment="center")
    ax.set_ylim(0, n_rows + 2)
    for i in range(n_rows):
        ax.text(0.3, n_rows - i, number_to_rowname(i + 1),
                verticalalignment="center",
                horizontalalignment="right")
    ax.plot([n_rows], [n_columns])


def place_inset_ax_in_data_coordinates(ax, bbox):
    """Return an ax inset in the given ax at the given bbox in
    data coordinates (bottom, left, width, height)"""

    bottom, left, width, height = bbox
    pixels_data_00 = ax.transData.transform([0, 0])
    pixels_data_wh = ax.transData.transform([width, height])
    iwidth, iheight = (pixels_data_wh - pixels_data_00) / ax.figure.dpi
    return inset_axes(
        ax, iwidth, iheight,
        loc=10,  # means "center"
        bbox_to_anchor=[bottom, left, width, height],
        bbox_transform=ax.transData
    )


class PlatePlotter:

    def plot_plate(self, plate, ax=None, well_condition=None,
                   progress_bar=False):
        if ax is None:
            fig, ax = plt.subplots(1, facecolor="white")
        if well_condition is None:
            well_condition = lambda well:  True

        draw_plate_layout(plate.num_wells, ax)

        stats = {}

        def progress(plate):
            if progress_bar:
                return tqdm(plate, total=plate.num_wells)
            else:
                return plate
        for well in progress(plate):
            if not well_condition(well):
                continue

            x, y = well.column, well.row
            y = plate.num_rows - y + 1

            stats[well.name] = self.plot_well(ax, x, y, well)

        self.post_process(ax, stats)
        return ax, stats

    def post_process(self, ax, stats):
        pass


class PlateColorsPlotter(PlatePlotter):

    def __init__(self, stat_function, with_colorbar=False):
        self.stat_function = stat_function
        self.with_colorbar = with_colorbar

    def plot_well(self, ax, x, y, well):
        return ((x, y), self.stat_function(well))

    def post_process(self, ax, stats):
        xy, stats = zip(*stats.values())
        xx, yy = zip(*xy)
        scatterplot = ax.scatter(xx, yy, s=120, c=stats)
        if self.with_colorbar:
            ax.figure.colorbar(scatterplot)


class PlateTextPlotter(PlatePlotter):

    def __init__(self, text_function, fontdict=None):

        self.fontdict = {} if fontdict is None else fontdict
        self.text_function = text_function

    def plot_well(self, ax, x, y, well):
        text = self.text_function(well)
        fontdict = self.fontdict
        if not isinstance(fontdict, dict):
            fontdict = fontdict(well)

        ax.text(x, y, str(text),
                fontdict=fontdict,
                horizontalalignment="center",
                verticalalignment="center")
        return ((x, y), text)


class PlateGraphsPlotter(PlatePlotter):
    """

    Parameters
    ----------

     well_plotter:

     subplot_size:
       (width, height) of subplots, between 0 and 1

    """

    def __init__(self, plot_function, subplot_size=(0.7, 0.7)):

        self.plot_function = plot_function
        self.subplot_size = subplot_size
        self.subplot_width = float(subplot_size[0])
        self.subplot_height = float(subplot_size[1])

    def plot_well(self, ax, x, y, well):
        bbox = (x - self.subplot_width / 2.0,
                y - self.subplot_height / 2.0,
                self.subplot_width,
                self.subplot_height)
        well_ax = place_inset_ax_in_data_coordinates(ax, bbox)
        self.plot_function(well, well_ax)
        return well_ax
