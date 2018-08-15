import copy

from plotly import tools
from plotly.offline import plot, iplot
import plotly.graph_objs as go
import json
import re
import numpy as np


# Defaults ###################################################################

PLOTLY_WIDTH = 850
PLOTLY_HEIGHT = 450
PLOTLY_HEIGHT_MULTI = 240

plotly_cfg_2d = {
    'showLink': False,
    'scrollZoom': True,
    #'displayModeBar': False,
    'editable': False,
    'doubleClick': 'reset+autosize',
    'modeBarButtonsToRemove': ['sendDataToCloud', 'zoomIn2d', 'zoomOut2d', 'autoScale2d'],
    'displaylogo': False,
}

xaxis_lhc = dict(
        range=[0, 27000],
        title="Position [m]",
        exponentformat="none",
    )

plotly_layout_default = go.Layout(
        autosize=False,
        width=PLOTLY_WIDTH,
        height=PLOTLY_HEIGHT,
        xaxis=dict(
            exponentformat="power",
            showgrid=True,
            titlefont=dict(
                size=20,
            ),
        ),
        yaxis=dict(
            exponentformat="power",
            showgrid=True,
            titlefont=dict(
                size=20,
            ),
        ),
        margin=dict(
            l=80,
            r=40,
            t=20,
            b=45,
        ),
        font=dict(
            size=13,
        ),
    )


# Plotting ###################################################################


def plotly_wrapper(data, layout, name, config=plotly_cfg_2d):
    """ A simple wrapper not create the figure first """
    fig = dict(data=data, layout=layout)
    iplot(fig, filename=name, config=config)


def plotly_wrapper_python(data, layout, name, config=plotly_cfg_2d):
    """ A simple wrapper not create the figure first """
    fig = dict(data=data, layout=layout)
    plot(fig, filename=name, config=config)


def plotly_from_json(file, name, config=plotly_cfg_2d):
    """ Loads from json file """
    with open(file, "r") as f:
        fig = json.loads(f.read())
    iplot(fig, filename=name, config=config)


# Figure Content #############################################################


def get_layout(**kwargs):
    """ Returns the standard layout updated by **kwargs """
    lo = copy.deepcopy(plotly_layout_default)
    for key in kwargs:
        if key not in lo or not isinstance(kwargs[key], dict):
            lo[key] = kwargs[key]
        else:
            lo[key].update(kwargs[key])
    return lo


def get_scatter_for_df(df, x_col=None, y_col=None, e_col=None, name="", legendgroup="", color=None):
    """ Returns a scatter object from Dataframe

    Works with dataframes containing 'Model', 'Value' and 'Error' columns"""
    if x_col is None:
        x_col = "S"

    if y_col is None:
        raise ValueError("Y-Column required!")

    scatter = go.Scatter(
        x=df[x_col].tolist(),
        y=df[y_col].tolist(),
        mode='lines',
        name=name,
        legendgroup=legendgroup,
        hoverinfo="x+y+text",
        hovertext=df.index.tolist(),
        line=dict(color=color),
    )

    if e_col is not None:
        scatter["error_y"] = dict(
            type='data',
            array=df[e_col].tolist(),
            thickness=1.5,
            width=3,
            opacity=0.5,
            color=color,
        )
    return scatter


def get_vertical_line(x, y, name, color='rgb(200, 200, 200)'):
    """ Returns a Scatter object of a vertrical line at scalar x going from y[0] to y[1]. """
    return go.Scatter(
        x=[x, x],
        y=y,
        mode='lines',
        name=name,
        legendgroup='vline',
        hoverinfo="x+name",
        showlegend=False,
        line=dict(
            color=color
        ),

    )


def get_horizontal_line(x, y, name, color='rgb(200, 200, 200)'):
    """ Returns a Scatter object of a vertrical line at scalar y going from x[0] to x[1]. """
    return go.Scatter(
        x=x,
        y=[y, y],
        mode='lines',
        name=name,
        legendgroup='hline',
        hoverinfo="x+name",
        showlegend=False,
        line=dict(
            color=color,
        ),

    )


def multi_plot(figs, same_data=True, same_axes=True, sync_x=False, sync_y=False, log_x=False, log_y=False):
    if len(figs) % 2:
        figs += [None]

    nfigs = len(figs)

    titles = []
    for fig in figs:
        try:
            titles.append(fig["layout"].get("title", None))
        except TypeError:
            titles.append(None)

    fig_multi = tools.make_subplots(rows=nfigs/2, cols=2,
                                    subplot_titles=titles, print_grid=False)

    sync = dict(x=sync_x, y=sync_y)
    log = dict(x=log_x, y=log_y)
    lim = dict(x=None, y=None)
    if any(sync.values()):
        for fig in figs:
            if fig is not None:
                for axis in ["x", "y"]:
                    current_range = fig['layout']['{}axis'.format(axis)].get('range', None)
                    if current_range is not None:
                        if lim[axis] is None:
                            lim[axis] = current_range
                        else:
                            lim[axis][0] = min([lim[axis][0], current_range[0]])
                            lim[axis][1] = max([lim[axis][1], current_range[1]])

    for idx_fig, fig in enumerate(figs):
        col = idx_fig % 2 + 1
        row = idx_fig / 2 + 1
        if fig is not None:
            for trace in fig["data"]:
                if same_data and trace.get('showlegend', True):
                    trace["legendgroup"] = trace["name"]
                    trace['showlegend'] = idx_fig == 0

                if re.match(r"IP\d", trace['name']) and sync_y:
                    if log_y:
                        trace["y"] = [1/lim["y"][1], lim["y"][1]]
                    else:
                        trace["y"] = lim['y']

                fig_multi.append_trace(trace, row, col)

            for axis in ["x", "y"]:
                new_axis = "{}axis{}".format(axis, idx_fig + 1)
                old_axis = "{}axis".format(axis)
                fig_multi["layout"][new_axis].update(fig['layout'][old_axis])
                fig_multi["layout"][new_axis]["titlefont"]["size"] = \
                    .8 * fig_multi["layout"][new_axis]["titlefont"]["size"]

                if same_axes:
                    if (axis == "x" and row != (nfigs/2)) or (axis == "y" and col != 1):
                        fig_multi["layout"][new_axis]["title"] = None

                if sync[axis]:
                    if log[axis]:
                        if lim[axis][0] > 0:
                            fig_multi["layout"][new_axis]['range'] = np.log10(lim[axis])
                        else:
                            fig_multi["layout"][new_axis]['range'] = [0, np.log10(lim[axis][1])]
                    else:
                        fig_multi["layout"][new_axis]['range'] = lim[axis]

                if log[axis]:
                    fig_multi["layout"][new_axis]['type'] = 'log'
                    # fig_multi["layout"][new_axis]['tick0'] = 0
                    fig_multi["layout"][new_axis]['dtick'] = 1

    fig_multi["layout"]["height"] = PLOTLY_HEIGHT_MULTI * nfigs/2

    tmp_layout = plotly_layout_default.copy()
    tmp_layout.pop("height")
    tmp_layout.pop("xaxis")
    tmp_layout.pop("yaxis")
    tmp_layout["width"] = 0.97 * PLOTLY_WIDTH
    fig_multi["layout"].update(tmp_layout)
    return fig_multi



