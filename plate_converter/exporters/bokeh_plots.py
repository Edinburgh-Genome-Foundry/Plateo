from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import (
    FixedTicker, Range1d, TapTool, Rect, CustomJS, HoverTool, OpenURL
)
from ..tools import (
    compute_rows_columns,
    dicts_to_columns,
    wellname_to_coordinates,
    number_to_rowname
)
import numpy as np


def bokeh_plot_plate(num_wells, wells, hover_fields=()):
    wells = [
        {
            k: v
            for k, v in well.items()
            if not isinstance(v, dict)
        }
        for well in wells
    ]

    n_rows, n_columns = compute_rows_columns(num_wells)
    p = figure(plot_width=600, plot_height=400, tools="box_zoom,reset,tap",
               x_range=Range1d(0, n_columns + 2), y_range=Range1d(0, n_rows + 2),
               responsive=True)

    placeholder_wells = p.circle(
        x="x", y="y", radius=0.3, fill_color=None,
        line_width=1, line_color="gray", name="placeholder_well",
        source=ColumnDataSource(dicts_to_columns([
            {
                "x": x + 2,
                "y": y + 1
            }
            for y in range(n_rows)
            for x in range(n_columns)
        ]))
    )

    dicts = []
    for well in wells:
        row, column = wellname_to_coordinates(well["well_name"])
        well_infos = {
            "display_color": "gray",
            "bokeh_x": column + 1,
            "bokeh_y": n_rows + 1 - row
        }
        well_infos.update(well)
        dicts.append(well_infos)

    actual_wells = p.circle(
        x="bokeh_x", y="bokeh_y", radius=0.3, fill_color='display_color',
        line_width=1, line_color="black", name="well",
        source=ColumnDataSource(dicts_to_columns(dicts))
    )

    text = p.text(
        x="x", y="y", text="text", text_baseline="middle",
        text_align="center", text_font_size="%dpx" % (
          0.8 * 144 / int(np.round(np.sqrt(num_wells / 6)))),
        source=ColumnDataSource(dicts_to_columns([
            {
                "text": number_to_rowname(i + 1),
                "x": 1,
                "y": n_rows - i
            }
            for i in range(n_rows)
        ] + [
            {
                "text": str(i + 1),
                "x": i + 2,
                "y": n_rows + 1
            }
            for i in range(n_columns)
        ]))
    )

    hover = HoverTool(
        names=["well"],
        tooltips="<u><b>@well_name</b></u><br/>" + " ".join(
            ["@%s" % field for field in hover_fields])
    )
    p.add_tools(hover)

    if any(("url" in well) for well in wells):
        taptool = p.select(type=TapTool)
        taptool.callback = OpenURL(url="@url")

    p.logo = None
    p.yaxis.visible = None
    p.xaxis.visible = None
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    return p
