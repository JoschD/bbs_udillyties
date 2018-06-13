from matplotlib import pyplot as plt, gridspec, rcParams
from utils.plotting.plot_tfs import get_marker
from utils.contexts import suppress_exception


def plot_wrapper(data, layout, title):
    # create figure
    fig = plt.figure()
    fig.canvas.set_window_title(title)
    gs = gridspec.GridSpec(1, 1, height_ratios=[1])
    ax = fig.add_subplot(gs)
    for idx, line in enumerate(data):
        e_val = None
        with suppress_exception(KeyError):
            e_val = data["error_y"]["array"]

        _, caps, bars = ax.errorbar(data["x"], data["y"], yerr=e_val,
                                    ls=rcParams[u"lines.linestyle"],
                                    fmt=get_marker(idx, True),
                                    label=data["name"])

        # loop through bars and caps and set the alpha value
        with suppress_exception(KeyError):
            [bar.set_alpha(data["error_y"]["opacity"]) for bar in bars]
            [cap.set_alpha(data["error_y"]["opacity"]) for cap in caps]

    with suppress_exception(KeyError):
        ax.set_ylabel(layout["yaxis"]["title"])

    with suppress_exception(KeyError):
        ax.set_xlabel(layout["xaxis"]["title"])

    with suppress_exception(KeyError):
        ax.set_ylim(layout["yaxis"]["range"])

    with suppress_exception(KeyError):
        ax.set_xlim(layout["xaxis"]["range"])

    return fig


def plot_and_save(path, data, layout, title):
    fig = plot_wrapper(data, layout, title)
    fig.tight_layout()
    fig.savefig(path, bbox_inches='tight')











