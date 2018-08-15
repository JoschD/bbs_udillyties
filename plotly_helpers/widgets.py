from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go

# Buttons ####################################################################


def get_rerange_button(x_range=None, y_range=None, name="Button", naxis=None):
    """ Returns a button that scales the plot to x_range, y_range """
    def get_arg(s, r):
        if r is not None:
            return {"{:s}.range".format(s): r}
        return {}

    arg = {}
    arg.update(get_arg('xaxis', x_range))
    arg.update(get_arg('yaxis', y_range))

    for idx in range(1, naxis+1):
        arg.update(get_arg('xaxis{:d}'.format(idx), x_range))
        arg.update(get_arg('yaxis{:d}'.format(idx), y_range))

    return dict(
        args=[arg],
        label=name,
        method='relayout'
    )