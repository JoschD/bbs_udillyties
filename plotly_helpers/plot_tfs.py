import json
import os
from udillyties.plotting import get_params, _check_opt, entrypoint, _get_data, _find_ir_pos, _get_auto_scale
from predefined import get_scatter_for_df, get_horizontal_line, get_layout, xaxis_lhc


@entrypoint(get_params(), strict=True)
def plot(opt):
    """ Plots multiple columns into one figure """
    # preparations
    opt = _check_opt(opt)
    twiss_data = _get_data(opt.files)

    if len(twiss_data) == 6:
        c = [
            'rgb(31, 119, 180)',  # muted blue
            'rgb(23, 190, 207)',  # blue-teal
            'rgb(188, 189, 34)',  # curry yellow-green
            'rgb(44, 160, 44)',  # cooked asparagus green
            'rgb(214, 39, 40)',  # brick red
            'rgb(255, 127, 14)',  # safety orange
            'rgb(140, 86, 75)',  # chestnut brown
            'rgb(227, 119, 194)',  # raspberry yogurt pink
            'rgb(127, 127, 127)',  # middle gray
            'rgb(148, 103, 189)',  # muted purple
        ]
    else:
        c = [
            'rgb(31, 119, 180)',  # muted blue
            'rgb(188, 189, 34)',  # curry yellow-green
            'rgb(44, 160, 44)',  # cooked asparagus green
            'rgb(214, 39, 40)',  # brick red
            'rgb(255, 127, 14)',  # safety orange
            'rgb(140, 86, 75)',  # chestnut brown
            'rgb(227, 119, 194)',  # raspberry yogurt pink
            'rgb(127, 127, 127)',  # middle gray
            'rgb(23, 190, 207)',  # blue-teal
            'rgb(148, 103, 189)',  # muted purple
        ]

    # plotting
    lines = []
    ir_pos = _find_ir_pos(twiss_data)
    for ir in ir_pos:
        lines.append(get_horizontal_line(ir_pos[ir], [-1000, 1000], ir))

    for idx, data in enumerate(twiss_data):
        try:
            data = data.set_index("NAME")
        except KeyError:
            pass

        e_col = None
        if opt.e_cols[0] in data.columns:
            e_col = opt.e_cols[0]
        legend = opt.legends[idx]

        scatter = get_scatter_for_df(data,
                                     x_col=opt.x_cols[0],
                                     y_col=opt.y_cols[0],
                                     e_col=e_col,
                                     name=legend,)
        scatter["visible"] = "legendonly" if legend.endswith("0") else True
        scatter["line"]["color"] = c[idx % len(c)]
        try:
            scatter["error_y"]["color"] = c[idx % len(c)]
        except KeyError:
            pass

        lines.append(scatter)
        if opt.auto_scale:
            current_y_lims = _get_auto_scale(data[opt.y_cols[0]], opt.auto_scale)
            if idx == 0:
                y_lims = current_y_lims
            else:
                y_lims = [min(y_lims[0], current_y_lims[0]),
                          max(y_lims[1], current_y_lims[1])]

    yaxis = {
        "title": os.path.basename(opt.output)
    }
    if opt.auto_scale:
        yaxis["range"] = y_lims
    layout = get_layout(xaxis=xaxis_lhc, yaxis=yaxis)

    fig = dict(data=lines, layout=layout)

    with open(opt.output + ".json", "w") as f:
        f.write(json.dumps(fig))

    return fig

