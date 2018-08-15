import math

from matplotlib import pyplot as plt, gridspec, rcParams
from matplotlib.backends.backend_pdf import PdfPages

from utils.contexts import suppress_exception
from utils.plotting import plot_style as ps


def plot_wrapper(data, layout, title):
    # create figure
    ps.set_style("standard", {u'grid.linestyle': u'--'})
    fig = plt.figure()
    fig.canvas.set_window_title(title)
    gs = gridspec.GridSpec(1, 1, height_ratios=[1])
    ax = fig.add_subplot(gs[0])
    color_idx = 0
    n_legend = 0
    for idx, line in enumerate(data):
        e_val = None
        with suppress_exception(KeyError):
            e_val = line["error_y"]["array"]

        color = ps.get_mpl_color(color_idx)
        color_idx += 1
        with suppress_exception([KeyError, IndexError]):
            if line["line"]["color"]:
                color = ps.rgb_plotly_to_mpl(line["line"]["color"])
                color_idx += -1

        marker = ""
        if "marker" in line["mode"]:
            marker = ps.MarkerList.get_marker(idx)

        ls = ""
        if "lines" in line["mode"]:
            ls = rcParams[u"lines.linestyle"]

        label = line["name"]
        n_legend += 1
        with suppress_exception(KeyError):
            if line["showlegend"] is not None and not line["showlegend"]:
                ax.text(x=line["x"][0],
                        y=line["y"][1] + (line["y"][1] - line["y"][0]) * 0.002,
                        s=label,
                        ha="center", va="bottom",
                        color=color,
                        )
                label = "_nolegend_"
                n_legend += -1

        _, caps, bars = ax.errorbar(line["x"], line["y"], yerr=e_val,
                                    ls=ls,
                                    marker=marker,
                                    label=label,
                                    color=color,
                                    )

        # loop through bars and caps and set the alpha value
        with suppress_exception(KeyError):
            [bar.set_alpha(line["error_y"]["opacity"]) for bar in bars]
            [cap.set_alpha(line["error_y"]["opacity"]) for cap in caps]

    with suppress_exception(KeyError):
        ax.set_ylabel(layout["yaxis"]["title"])

    with suppress_exception(KeyError):
        ax.set_xlabel(layout["xaxis"]["title"])

    with suppress_exception(KeyError):
        ax.set_ylim(layout["yaxis"]["range"])

    with suppress_exception(KeyError):
        ax.set_xlim(layout["xaxis"]["range"])

    with suppress_exception(KeyError):
        ax.xaxis.grid(layout["xaxis"]["showgrid"])

    with suppress_exception(KeyError):
        ax.yaxis.grid(layout["yaxis"]["showgrid"])

    ncol = 3
    nlines_legend = math.ceil(n_legend / 3.)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1. + nlines_legend * 0.1),
              fancybox=True, shadow=True, ncol=ncol)

    return fig


def plot_and_save(path, data, layout, title):
    fig = plot_wrapper(data, layout, title)
    mpdf = PdfPages(path)
    fig.tight_layout()
    mpdf.savefig(figure=fig, bbox_inches='tight')
    mpdf.close()
    # plt.show()
    plt.close()











