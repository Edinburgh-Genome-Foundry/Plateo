import textwrap

import numpy as np

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from mpl_toolkits.axes_grid.inset_locator import inset_axes
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
from tqdm import tqdm

from ..tools import (
    compute_rows_columns,
    number_to_rowname
)

letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def draw_plate_layout(num_wells, ax):
    """Draw the plate's border, row letters, column numbers."""
    n_rows, n_columns = compute_rows_columns(num_wells)
    ax.axis("off")
    ax.add_patch(patches.Rectangle((0.5, 0.5), n_columns, n_rows, fill=False))
    for i in range(1, n_columns + 1):
        ax.text(i, 1.075 * n_rows, str(i), horizontalalignment="center")
    ax.set_ylim(0, n_rows + 2)
    for i in range(n_rows):
        ax.text(0.3, n_rows - i, number_to_rowname(i + 1),
                verticalalignment="center",
                horizontalalignment="right")
    ax.plot([n_rows], [n_columns])
    ax.set_xlim(0, n_columns + 0.6)


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
    """Base class for all matplotlib-based plate plotters
    """

    def plot_plate(self, plate, ax=None, well_filter=None,
                   progress_bar=False, figsize=(10, 5)):
        """Plot the plate using Matplotlib.

        Parameters
        ----------

        plate
          The plate object to be plotted.

        ax
          The Matplotlib ax on which to plot. If none is provided, one will
          be created (and returned at the end)

        well_filter
          Function f(well)=>true/false. Wells returning false will not be
          considered.

        progress_bar
          If true, display a progress bar while plotting.

        figsize
          Size of the figure, width/height in inches.


        Returns
        -------

        ax, stats
          The matplotlib ax on which the figure was plotted, and the computed
          stats in format {wellname: well_stat}, (if relevant)
        """

        if not MATPLOTLIB_AVAILABLE:
            raise IOError("Install Matplotlib to be able to plot")
        if ax is None:
            fig, ax = plt.subplots(1, facecolor="white", figsize=figsize)
        if well_filter is None:
            well_filter = lambda well:  True

        draw_plate_layout(plate.num_wells, ax)

        stats = {}

        def progress(plate):
            if progress_bar:
                return tqdm(plate, total=plate.num_wells)
            else:
                return plate
        for well in progress(plate):
            if not well_filter(well):
                continue

            x, y = well.column, well.row
            y = plate.num_rows - y + 1

            stats[well.name] = self.plot_well(ax, x, y, well)

        self.post_process(ax, stats)
        return ax, stats

    def post_process(self, ax, stats):
        pass


class PlateColorsPlotter(PlatePlotter):
    """Plot a plate's well statistic with wells colored differently.

    Parameters
    ----------

    stat_function
      The function to be plotted, with signature (well) => value

    with_colorbar
      It true a colorbar giving a scale for color values will be plotted
      alongside the map

    """

    def __init__(self, stat_function, colormap=None, plot_colorbar=False,
                 well_radius='full', vmin=None, vmax=None, alpha=1.0,
                 edge_width=1):
        self.stat_function = stat_function
        self.colormap = colormap
        self.plot_colorbar = plot_colorbar
        self.well_radius = well_radius
        self.alpha = alpha
        self.vmin = vmin
        self.vmax = vmax
        self.edge_width = edge_width

    def plot_well(self, ax, x, y, well):
        return ((x, y), self.stat_function(well))

    def post_process(self, ax, stats):
        xy, stats_values = zip(*stats.values())
        xx, yy = zip(*xy)
        if self.well_radius == 'full':
            values = list(stats.values())
            colors = [
                v[1] for v in values if (v[1] is not None)
            ]
            depth = len(colors[0]) if hasattr(colors[0], '__iter__') else 1
            my, mx = max(yy), max(xx)
            grid = np.zeros((my, mx, depth) if depth > 1 else (my, mx))
            for (x, y), stat in stats.values():
                grid[y-1, x-1] = stat
            plot = ax.imshow(grid[::-1, :], alpha=self.alpha,
                             vmin=self.vmin, vmax=self.vmax,
                             cmap=self.colormap,
                             extent=[0.5, max(xx)+0.5, 0.5, max(yy)+0.5])


        else:
            plot = ax.scatter(xx, yy, s=self.well_radius, c=stats_values,
                              vmin=self.vmin, vmax=self.vmax,
                              linewidths=self.edge_width,
                              edgecolors='k',
                              alpha=self.alpha, cmap=self.colormap)
        if self.plot_colorbar:
            ax.figure.colorbar(plot)


class PlateTextPlotter(PlatePlotter):
    """Plot a plate's well statistic as text at the well's positions.

    Parameters
    ----------

    text_function
      A function (well) => text

    with_colorbar
      It true a colorbar giving a scale for color values will be plotted
      alongside the map
    """

    def __init__(self, text_function, line_length=None, fontdict=None):

        self.fontdict = {} if fontdict is None else fontdict
        self.text_function = text_function
        self.line_length = line_length

    def plot_well(self, ax, x, y, well):
        text = str(self.text_function(well))
        if self.line_length is not None:
            text = '\n'.join(textwrap.wrap(text, self.line_length))
        fontdict = self.fontdict
        if not isinstance(fontdict, dict):
            fontdict = fontdict(well)

        ax.text(x, y, str(text),
                fontdict=fontdict,
                horizontalalignment="center",
                verticalalignment="center")
        return ((x, y), text)


class PlateGraphsPlotter(PlatePlotter):
    """Plot a graph (for instance time series) for each well of the plate

    The result has the shape of a plate, with each well replaced by a graph.

    Parameters
    ----------

     plot_function
       A function f(well, well_ax) which plots something on the provided
       ``well_ax`` depending on the ``well``.

     subplot_size
       (width, height) of subplots, between 0 and 1 (1 meaning the graphs of
       the different wells will have virtually no margin between them)

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
