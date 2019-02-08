import math
import json
import os

from matplotlib import pyplot as plt, gridspec, rcParams
from matplotlib.backends.backend_pdf import PdfPages

from utils.contexts import suppress_exception
from plotshop import plot_style as ps


def plot_wrapper(data, layout, title, legend_cols=3, fig=None):
    tick_length_before_rotation = 6
    # create figure
    if fig is None:
        fig = plt.figure()
        gs = gridspec.GridSpec(1, 1, height_ratios=[1])
        ax = fig.add_subplot(gs[0])
    else:
        ax = fig.gca()
    fig.canvas.set_window_title(title)
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
        if layout["yaxis"]["title"] is not None:
            ax.set_ylabel(layout["yaxis"]["title"])

    with suppress_exception(KeyError):
        if layout["xaxis"]["title"] is not None:
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
        if layout["xaxis"]["tickvals"] is not None:
            ax.xaxis.set_ticks(layout["xaxis"]["tickvals"])

    with suppress_exception(KeyError):
        if layout["xaxis"]["ticktext"] is not None:
            max_len = max([len(txt) for txt in layout["xaxis"]["ticktext"]])
            rot = 45 if max_len > tick_length_before_rotation else 0
            ha = "right" if max_len > tick_length_before_rotation else "center"
            ax.xaxis.set_ticklabels(layout["xaxis"]["ticktext"], rotation=rot, ha=ha)

    with suppress_exception(KeyError):
        if layout["xaxis"]["showticklabels"] is not None and not layout["xaxis"]["showticklabels"]:
            ax.set_xticklabels(['']*len(list(ax.get_xticklabels())))

    with suppress_exception(KeyError):
        if layout["yaxis"]["tickvals"] is not None:
            ax.yaxis.set_ticks(layout["yaxis"]["tickvals"])

    with suppress_exception(KeyError):
        if layout["yaxis"]["ticktext"] is not None:
            max_len = max([len(txt) for txt in layout["yaxis"]["ticktext"]])
            rot = 45 if max_len > tick_length_before_rotation else 0
            ha = "right" if max_len > tick_length_before_rotation else "center"
            ax.yaxis.set_ticklabels(layout["yaxis"]["ticktext"], rotation=rot, ha=ha)

    with suppress_exception(KeyError):
        if layout["yaxis"]["showticklabels"] is not None and not layout["yaxis"]["showticklabels"]:
            ax.set_yticklabels(['']*len(list(ax.get_yticklabels())))

    if legend_cols > 0:
        leg = ps.make_top_legend(ax, legend_cols)
    # use _set_loc, makes finding the location later on easier
    # leg._set_loc((-.7 if n_legend == 1 else -.88, 1.05))
    # fig.tight_layout()

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
    return plot_wrapper(content_dict["data"], content_dict["layout"], title)


# Script Mode ##################################################################


if __name__ == '__main__':
    plot_from_json("/home/jdilly/link_afs_work/private/STUDY.18.ampdet_flatoptics/plot_output/B1.noXing.errors.B4.in.all.IPs.ANHX0100.json")
    plt.show()









