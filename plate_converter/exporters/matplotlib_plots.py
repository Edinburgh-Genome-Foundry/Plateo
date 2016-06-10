import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from ..tools import (
    compute_rows_columns,
    wellname_to_coordinates,
    number_to_rowname
)

letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def wellname2pos(wellname):
    x = int(wellname[1:])
    y = 8 - letters.index(wellname[0])
    return (x, y)


def draw_plate_layout(num_wells, ax):
    n_rows, n_columns = compute_rows_columns(num_wells)
    ax.axis("off")
    ax.add_patch(patches.Rectangle((0.5, 0.5), n_columns, n_rows, fill=False))
    for i in range(1, n_columns + 1):
        ax.text(i, 8.6, str(i), horizontalalignment="center")
    ax.set_ylim(0, n_rows + 2)
    for i in range(n_rows):
        ax.text(0.3, n_rows - i, number_to_rowname(i),
                verticalalignment="center",
                horizontalalignment="right")
    ax.plot([n_rows], [n_columns])


def plot_plate_statistic_matplotlib(plate_layout, statistic, ax=None,
                                    mode="text", fontsize=8, colorbar=True):
    if ax is None:
        fig, ax = plt.subplots(1, facecolor="white")
    draw_plate_layout(plate_layout.num_wells, ax)

    if mode == "color":

        xy_stat = []
        for wellname, result in plate_layout.items():
            x, y = wellname2pos(wellname)
            stat = statistic(result)
            if stat is not None:
                xy_stat.append(((x, y), stat))
        xy, stats = zip(*xy_stat)
        xx, yy = zip(*xy)
        scatterplot = ax.scatter(xx, yy, s=120, c=stats)
        if colorbar:
            ax.figure.colorbar(scatterplot)

    elif mode == "text":

        for wellname, result in plate_layout.wells.items():
            x, y = wellname2pos(wellname)
            stat = statistic(result)
            ax.text(x, y, str(stat), fontdict={"size": fontsize},
                    horizontalalignment="center",
                    verticalalignment="center")

    ax.figure.tight_layout()
    return ax
