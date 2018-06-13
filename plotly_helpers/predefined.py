import copy

from plotly.offline import plot, iplot
import plotly.graph_objs as go
import json


# Defaults ###################################################################

PLOTLY_WIDTH = 850
PLOTLY_HEIGHT = 450

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


def get_scatter_for_df(df, x_col=None, y_col=None, e_col=None, name="", legendgroup=""):
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
    )

    if e_col is not None:
        scatter["error_y"] = dict(
            type='data',
            array=df[e_col].tolist(),
            thickness=1.5,
            width=3,
            opacity=0.5,
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


























