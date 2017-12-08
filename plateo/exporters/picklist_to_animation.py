"""Module to produce animations of the picklist (one image per transfer).


**Organization:**

.. mermaid::

    graph TD
    pt[plot_transfer]
    lsatp[list_source_and_target_plates]
    mtf[make_transfer_figure]
    a[animate]
    wpdf[write_pdf]
    mf[message_function]
    mplftnpim[mplfig_to_npimage]
    pp[plot_plates]

    lsatp --> pp
    pp --> pt
    pt -->mtf
    mf --> mtf
    mtf --> wpdf
    mplftnpim --> a
    mtf --> a
"""


from matplotlib.patches import ConnectionPatch
from proglog import ProgressBarLogger, TqdmProgressBarLogger
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import imageio


class PicklistAnimator:
    """A picklist animator !

    Parameters
    ----------
    plate_plotters
      A dictionnary ``{plate_name: plotter_to_use_for_that_plate}``
      Where the plotter is a Plateo PlatePlotter.

    message_function
      A function ``(picklist, transfer) => string`` taking as input a Plateo
      Picklist and Transfer objects.

    logger
      Either None for no logger, 'bar' for a progress bar logger, or any custom
      Proglog progress bar logger.


    Examples
    --------

    >>> animator = PicklistAnimator(
    >>>     plate_plotters={
    >>>         'Source_1': success_plotter,
    >>>         'Source_2': success_plotter,
    >>>         'Target': volume_plotter
    >>>     },
    >>>     logger=TqdmProgressBarLogger(bars=['transfers'])
    >>> )
    >>> animator.animate(picklist, "test.mp4", fps=3)


    """

    def __init__(self, plate_plotters, message_function=None,
                 plate_figure_size=(8, 6), logger='bar'):
        """Initialize."""
        self.plate_plotters = plate_plotters
        if logger is None:
            logger = ProgressBarLogger()
        elif logger == 'bar':
            logger = TqdmProgressBarLogger(bars=['transfers'])
        self.logger = logger
        self.message_function = message_function
        self.plate_figure_size = plate_figure_size

    @staticmethod
    def mplfig_to_npimage(fig):
        """ Converts a matplotlib figure to a RGB array"""
        #  only the Agg backend now supports the tostring_rgb function
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        l, b, w, h = canvas.figure.bbox.bounds
        w, h = int(w), int(h)
        buf = canvas.tostring_rgb()
        image = np.fromstring(buf, dtype=np.uint8)
        return image.reshape(h, w, 3)

    @staticmethod
    def list_source_and_target_plates(picklist):
        """Return two lists: plates with resp. source wells and target wells.

        In the final animation, source plates will be on the left and target
        plates on the right.
        """
        source_plates = []
        target_plates = []
        seen_plates = set()
        for _transfer in picklist.transfers_list:
            source_plate = _transfer.source_well.plate
            target_plate = _transfer.destination_well.plate
            if source_plate not in seen_plates:
                source_plates.append(source_plate)
            if target_plate not in seen_plates:
                target_plates.append(target_plate)
            seen_plates.add(source_plate)
            seen_plates.add(target_plate)
        return source_plates, target_plates

    def plot_plates(self, source_plates, target_plates, axes=None):
        """Plot all plates, sources on the left, targets on the right.

        Parameters
        ----------

        source_plates
          List of plates with (at least mostly) source wells.

        target_plates
          List of plates with (at least mostly) destination wells.

        axes
          (left, right): Two lists of matplotlib axes, one for the source
          plates on the left, one for the destination plates on the right.

        """
        if axes is None:
            max_rows = max(len(source_plates), len(target_plates))
            w, h = self.plate_figure_size
            fig, axes = plt.subplots(max_rows, 2,
                                     figsize=(2 * w, h * max_rows))
            if max_rows == 1:
                axes = np.array([axes])
            for ax in axes.flatten():
                ax.axis('off')
                ax.set_aspect('equal')
        else:
            fig = axes[0][0].figure
            for ax in axes.flatten():
                ax.clear()
                ax.axis('off')
                ax.set_aspect('equal')

        axes_dict = {}
        for c, plates in enumerate([target_plates, source_plates]):
            for i, plate in enumerate(plates):
                column = 1 - c
                ax = axes[i, column]
                ax.set_title(plate.name, fontsize=20)
                self.plate_plotters[plate.name].plot_plate(plate, ax=ax)
                axes_dict[plate.name] = ax
        for i in range(5):
            fig.tight_layout()
        return fig, axes, axes_dict

    def plot_transfer(self, transfer, source_plates, target_plates, axes=None):
        """Plot the plates and add and arrow for the transfer"""
        fig, axes, axes_dict = self.plot_plates(source_plates, target_plates,
                                                axes=axes)

        source_well = transfer.source_well
        source_plate = source_well.plate
        source_ax = axes_dict[source_plate.name]
        x, y = source_well.coordinates[::-1]
        source_coord = x, source_plate.num_rows - y + 1

        target_well = transfer.destination_well
        target_plate = target_well.plate
        target_ax = axes_dict[target_plate.name]
        x, y = target_well.coordinates[::-1]
        target_coord = x, target_plate.num_rows - y + 1

        target_ax.set_zorder(source_ax.get_zorder() - 1)
        arrow = ConnectionPatch(
            xyA=source_coord, xyB=target_coord,
            coordsA="data", coordsB="data",
            axesA=source_ax, axesB=target_ax,
            shrinkB=5.0, lw=2,
            facecolor='black',
            arrowstyle="wedge", zorder=1000)
        source_ax.add_artist(arrow)
        return fig, axes

    def _make_transfer_figure(self, picklist, transfer=None, axes=None):
        sources, targets = self.list_source_and_target_plates(picklist)
        if transfer is not None:
            index = self.logger.bars['transfers']['index']
            self.logger(transfers__index=index + 1)
            fig, axes = self.plot_transfer(transfer, sources, targets,
                                           axes=axes)
        else:
            fig, axes, _ = self.plot_plates(sources, targets)

        if self.message_function is not None:
            message = self.message_function(picklist, transfer)
            if message is not None:
                fig.subplots_adjust(top=0.8)
                fig.suptitle(message, fontsize=12)
        return fig, axes

    def animate(self, picklist, target, dpi=160, fps=5):
        """Create a movie of the picklist.

        Parameters
        ----------
        picklist
          Picklist to be animated

        target
          File path or file-like object where to write the movie.

        dpi
          Resolution of the image. The larger the dpi, the larger the image.

        fps
          Frames per second
        """
        self.logger(transfers__total=len(picklist.transfers_list))
        writer = imageio.get_writer(target, fps=fps)
        fig, axes = self._make_transfer_figure(picklist)

        def make_frame(picklist, transfer):
            fig, _ = self._make_transfer_figure(picklist, transfer, axes=axes)
            fig.dpi = dpi
            writer.append_data(self.mplfig_to_npimage(fig))
        picklist.execute(inplace=False, callback_function=make_frame)
        writer.close()
        plt.close(fig)

    def write_pdf(self, picklist, target):
        """Create a multi-page PDF animation of the picklist.

        Parameters
        ----------


        """
        self.logger(transfers__total=len(picklist.transfers_list))

        with PdfPages(target) as pdf:
            fig, axes = self._make_transfer_figure(picklist)

            def make_frame(picklist, transfer):
                fig, _ = self._make_transfer_figure(picklist, transfer, axes=axes)
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)
            picklist.execute(inplace=False, callback_function=make_frame)
