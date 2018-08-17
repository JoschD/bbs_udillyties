import math
import json
import os

from matplotlib import pyplot as plt, gridspec, rcParams
from matplotlib.backends.backend_pdf import PdfPages

from utils.contexts import suppress_exception
from utils.plotting import plot_style as ps


def plot_wrapper(data, layout, title):
    tick_length_before_rotation = 6
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

    with suppress_exception(KeyError):
        ax.xaxis.set_ticks(layout["xaxis"]["tickvals"])

    with suppress_exception(KeyError):
        max_len = max([len(txt) for txt in layout["xaxis"]["ticktext"]])
        rot = 45 if max_len > tick_length_before_rotation else 0
        ha = "right" if max_len > tick_length_before_rotation else "center"
        ax.xaxis.set_ticklabels(layout["xaxis"]["ticktext"], rotation=rot, ha=ha)

    with suppress_exception(KeyError):
        ax.yaxis.set_ticks(layout["yaxis"]["tickvals"])

    with suppress_exception(KeyError):
        max_len = max([len(txt) for txt in layout["yaxis"]["ticktext"]])
        rot = 45 if max_len > tick_length_before_rotation else 0
        ha = "right" if max_len > tick_length_before_rotation else "center"
        ax.yaxis.set_ticklabels(layout["yaxis"]["ticktext"], rotation=rot, ha=ha)

    ncol = 3
    nlines_legend = math.ceil(n_legend / 3.)
    leg = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1. + nlines_legend * 0.1),
              fancybox=True, shadow=True, ncol=ncol)
                # use _set_loc, makes finding the location later on easier
    leg._set_loc((.3 if n_legend == 1 else .12, 1.05))
    fig.tight_layout()

    return fig


def plot_and_save(path, data, layout, title):
    fig = plot_wrapper(data, layout, title)
    mpdf = PdfPages(path)
    fig.tight_layout()
    mpdf.savefig(figure=fig, bbox_inches='tight')
    mpdf.close()
    # plt.show()
    plt.close()


def plot_from_json(file_path):
    with open(file_path, "r") as f:
        content_dict = json.loads(f.read())
    title = os.path.basename(file_path.replace(".json", "")).replace(".", " ")
    plot_wrapper(content_dict["data"], content_dict["layout"], title)


# Script Mode ##################################################################


if __name__ == '__main__':
    plot_from_json("/home/jdilly/link_afs_work/private/STUDY.18.ampdet_flatoptics/plot_output/B1.noXing.errors.B4.in.all.IPs.ANHX0100.json")
    plt.show()









