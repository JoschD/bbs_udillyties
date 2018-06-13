from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go

# Buttons ####################################################################


def get_rerange_button(x_range, y_range, name):
    """ Returns a button that scales the plot to x_range, y_range """
    return dict(
        args=[{'xaxis.range': x_range, 'yaxis.range': y_range}],
        label=name,
        method='relayout'
    )