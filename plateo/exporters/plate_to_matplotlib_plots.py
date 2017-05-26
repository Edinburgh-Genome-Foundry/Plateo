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
                   progress_bar=False, figsize=(10,5)):
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
    """Plot a plate's well statistic as text at the well's positions.

    Parameters
    ----------

    text_function
      A function (well) => text

    with_colorbar
      It true a colorbar giving a scale for color values will be plotted
      alongside the map
    """

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
