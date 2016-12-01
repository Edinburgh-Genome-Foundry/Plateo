from copy import deepcopy

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


def plate_to_bokeh_plot(plate, hover_metadata=(), well_to_html=None,
                        well_color_function=None):
    wells = deepcopy(plate.wells)

    if well_color_function is None:
        def well_color_function(well):
            return "#fff" if well.content == {} else "#aaa"

    if hover_metadata != ():
        def well_to_html(well):
            return "\n".join(
                [well.name] + [
                    "%s: %s" % (field, well.metadata.get(field, ""))
                    for field in hover_metadata
                ]
            )
    elif well_to_html is None:
        well_to_html = lambda well: well.name

    for name, well in wells.items():
        well.metadata = {
            field: info
            for field, info in well.metadata.items()
            if not isinstance(info, dict)
        }

    n_rows, n_columns = plate.num_rows, plate.num_columns
    p = figure(plot_width=600, plot_height=400,
               tools="box_zoom,reset,tap,save",
               x_range=Range1d(0, n_columns + 2),
               y_range=Range1d(0, n_rows + 2),
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
    for name, well in wells.items():
        row, column = wellname_to_coordinates(name)
        well_infos = {
            "display_color": well_color_function(well),
            "bokeh_x": column + 1,
            "bokeh_y": n_rows + 1 - row,
            "html_content": well_to_html(well)
        }
        #well_infos.update(well.metadata)
        dicts.append(well_infos)

    actual_wells = p.circle(
        x="bokeh_x", y="bokeh_y", radius=0.3, fill_color='display_color',
        line_width=1, line_color="black", name="well",
        source=ColumnDataSource(dicts_to_columns(dicts))
    )

    text = p.text(
        x="x", y="y", text="text", text_baseline="middle",
        text_align="center", text_font_size="%dpx" % (
          0.8 * 144 / int(np.round(np.sqrt(plate.num_wells / 6)))),
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
    if well_to_html is not None:
        tooltips = "@html_content"
    else:
        tooltips = "<u><b>@well_name</b></u><br/>" + " ".join(
            ["@%s" % field for field in hover_metadata]
        )
    hover = HoverTool(names=["well"], tooltips=tooltips)
    p.add_tools(hover)

    if any(("url" in well) for well in wells):
        taptool = p.select(type=TapTool)
        taptool.callback = OpenURL(url="@url")

    p.toolbar.logo = None
    p.yaxis.visible = False
    p.xaxis.visible = False
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    return p
