import os
import shutil
import sys

import numpy as np
import pandas
import json
import plotly.graph_objs as go

# Beta-Beat Repo imports
beta_beta_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.append(beta_beta_path)

from utils.entrypoint import entrypoint
from utils import logging_tools
from utils import iotools
from plotshop import plot_style as ps
import irnl18_triplet_correction as tripcor
import irnl18_triplet_correction_template_control as tripcor_tmplt
from tfs_files import tfs_pandas as tfs
import udillyties.plotly_helpers.predefined as plotly_predef
import udillyties.plotly_helpers.matplotlib_wrapper as mpl_wrap
from matplotlib import pyplot as plt, gridspec, colors

LOG = logging_tools.get_logger(__name__)


AMPDET_FILENAME = "ptc_normal.ampdet.b{beam:d}.{id:s}.dat"  # see madx_snippets.py
AMPDET_NAMES = ["ANHX1000", "ANHY0100", "ANHX0100"]

LABEL_FORMAT = r"\unsansmath $\partial Q_{}/\partial 2J_{} \, \left[10^4 {{\mathrm{{m}}^{{-1}}}} \right]$ \sansmath"
# LABEL_FORMAT = r"$\partial Q_{}/\partial 2J_{} \, \left[ {{\mathrm{{m}}^{{-1}}}} \right]$"
YLABEL_MAP = {
    "ANHX1000": LABEL_FORMAT.format('x', 'x'),
    "ANHY1000": LABEL_FORMAT.format('y', 'x'),
    "ANHX0100": LABEL_FORMAT.format('x', 'y'),
    "ANHY0100": LABEL_FORMAT.format('y', 'y')
}

SAME_OPTICS = "same_optics"  # identifyier to be replaced by optics in filename
DEFAULT_OPTICS = "3030"  # optics to compare the correction by

# plotting order so histograms look nice
PLOT_STAGE_ORDER = ["errors_all", "errors_ip", "errors_mqx", "errors_mb_ip", "corrected", "errors_arc", "nominal"]


# plotting style corrections
MANUAL_STYLE_NORMAL = {u'figure.figsize': [6.4, 4.8], u'grid.linestyle': u'--',
                       u'errorbar.capsize': 2,
                       u'text.usetex': True,
                       u'text.latex.preamble': [
                                               # r'\usepackage{siunitx}',   # i need upright \micro symbols, but you need...
                                               # r'\sisetup{detect-all}',   # ...this to force siunitx to actually use your fonts
                                               r'\usepackage{helvet}',    # set the normal font here
                                               r'\usepackage{sansmath}',  # load up the sansmath so that math -> helvet
                                               r'\sansmath'               # <- tricky! -- gotta actually tell tex to use!
                                               ],
                       }
PLOT_STYLE = "standard"
# MANUAL_STYLE_NORMAL = {u'figure.figsize': [8.00, 8.00], u'grid.linestyle': u'--', u'errorbar.capsize': 2}
# PLOT_STYLE = "presentation"
MANUAL_STYLE_HIST = {u'figure.figsize': [10.80, 19.20], u'axes.grid': False}
MANUAL_STYLE_CTA = {u'figure.figsize': [7.5, 4.5], u'axes.grid': False, u'grid.alpha': 0}

LEGEND_COLS = 0

CORRECTED_BY_OUTPUT = False


# Quick Hacks ##############################################
HACKS = True

minmaxdict = {
    "A5": {"min": -2.7000, "max": 2.5000},
    "A6": {"min": -6.0000, "max": 3.0000},
    "B4": {"min": -15.0000, "max": 15.5000},
    "B5": {"min": -5.0000, "max": 7.0000},
    "B6": {"min": -10.0000, "max": 70.000},
    "B5A5B6A6": {"min": -9.0000, "max": 12.0000},
    "B4B5A5B6A6": {"min": -19.0000, "max": 25.0000},
}


legend_map = {
    "noXing": "Flat-Orbit",
    "wXing_in_IP1": "IP1 Crossing",
    "wXing_in_IP5": "IP5 Crossing",
    "wXing_in_IP5_IP1": "IP1 & IP5 Crossing",
}


color_index = ["noXing", "wXing_in_IP5", "wXing", "wXing_in_IP1"]

measurement_dict = {
    "b1_noXing_ANHX1000": [1600, 1100],
    "b1_wXing_in_IP5_ANHX1000": [112200, 12000],
    "b1_wXing_ANHX1000": [67270, 1815],

    "b1_noXing_ANHX0100": [8100, 27800],
    "b1_wXing_in_IP5_ANHX0100": [78500, 30100],
    "b1_wXing_ANHX0100": [17666, 1011],

    "b1_noXing_ANHY1000": [10300, 900],
    "b1_wXing_in_IP5_ANHY1000": [-8900, 16000],
    "b1_wXing_ANHY1000": [7554, 1745],

    "b1_noXing_ANHY0100": [-6200, 2800],
    "b1_wXing_in_IP5_ANHY0100": [6000, 3500],
    "b1_wXing_ANHY0100": [-75368, 1703],

    "b2_noXing_ANHX1000": [-14900, 1100],
    "b2_wXing_in_IP5_ANHX1000": [3200, 1000],
    "b2_wXing_ANHX1000": [-8517, 1536],

    "b2_noXing_ANHX0100": [-2400, 1200],
    "b2_wXing_in_IP5_ANHX0100": [-3800, 2600],
    "b2_wXing_ANHX0100": [-14361, 3471],

    "b2_noXing_ANHY1000": [7600, 2500],
    "b2_wXing_in_IP5_ANHY1000": [4100, 1400],
    "b2_wXing_ANHY1000": [-1447, 894],

    "b2_noXing_ANHY0100": [12400, 1500],
    "b2_wXing_in_IP5_ANHY0100": [25200, 2400],
    "b2_wXing_ANHY0100": [29439, 6476],
}


def hack_axis(xaxis, yaxis, current_params):
    if not HACKS:
        return
    etypes = "".join(current_params["error_types"])
    try:
        range = minmaxdict[etypes]
        yaxis.update(dict(range=[range["min"], range["max"]]))
    except KeyError:
        pass

    # if current_params["beam"] == 1:
    #     xaxis.update(dict(showticklabels=False))

    # if current_params["ampdet"] != "ANHX1000":
    #     yaxis.update(dict(showticklabels=False))
    #     MANUAL_STYLE_NORMAL.update({u"figure.figsize": [8., 8.]})
    # else:
    #     MANUAL_STYLE_NORMAL.update({u"figure.figsize": [8.5, 8.]})


def get_colors():
    """ Insert a new color for line 2 to fit to measurements"""
    if not HACKS:
        return ps.get_mpl_color()
    return (ps.get_mpl_color(i) for i in [0, 3, 1, 2, 4, 5, 6])


def add_measurement_lines(ax, current_data, lines):
    """ Add horizontal lines to represent measurement data. """
    acd_corr = 1 if current_data["ampdet"] in ["ANHX0100", "ANHY1000"] else .5
    for line in lines:
        line = line.replace("_in_IP5_IP1", "")
        id = "_".join(["b{:d}".format(current_data["beam"]), line, current_data["ampdet"]])
        try:
            measdata = measurement_dict[id]
        except KeyError:
            pass
        else:
            low = (measdata[0] - measdata[1]) * acd_corr * 1e-4
            upp = (measdata[0] + measdata[1]) * acd_corr * 1e-4
            color = colors.to_rgba(ps.get_mpl_color(color_index.index(line)), .3)
            ax.fill_between([0, len(PLOT_STAGE_ORDER)], 2 * [upp], 2 * [low],
                            facecolor=color)
            ax.plot([0, len(PLOT_STAGE_ORDER)], 2 * [measdata[0]*acd_corr*1e-4], '--', color=color[0:3])


# Entrypoint ###############################################


def get_params():
    """ Same params as in the creation of the files """
    return tripcor.get_params()


@entrypoint(get_params(), strict=True)
def gather_all_data(opt):
    """ Main function for separate plots for ampdet terms """
    LOG.info("Starting main evaluation loop.")
    opt = tripcor.check_opt(opt)
    # main loop
    for beam, xing, error_types, error_loc in main_loop(opt):
        _gather_data(opt.cwd, opt.machine, beam, xing, error_types, error_loc,
                     opt.optic_types, opt.seeds, opt.unused_stages)


@entrypoint(get_params(), strict=True)
def plot_optic_types_oneplot(opt):
    """ Main function for separate plots for optic types """
    for output_folder, data, current_params in main_body(opt):
        _plot_separate_ampdet(output_folder, data, current_params, opt.optic_types,
                              id="all_optics")


@entrypoint(get_params(), strict=True)
def plot_ampdetterms_oneplot(opt):
    """ Main function for single plot for optic types """
    for output_folder, data, current_params in main_body(opt):
        for otype in opt.optic_types:
            current_params.update(dict(otype=otype))
            _plot_all_ampdets_in_one(output_folder, data, current_params)


@entrypoint(get_params(), strict=True)
def plot_crossing_oneplot(opt):
    """ Main function to put all crossing into one plot. """
    LOG.info("Starting crossing evaluation loop.")
    opt = tripcor.check_opt(opt)
    output_folder = get_plot_output_folder(opt.cwd)

    # for beam in opt.beams:
    #     for otype in opt.optic_types:
    #         for error_types in opt.error_types:
    #             for error_loc in opt.error_locations:
    #                 for xing in opt.xing:
    #                     current_params = dict(beam=beam, optic_type=otype, error_types=error_types,
    #                                           error_loc=error_loc, xing=xing)
    #                     _update_min_max(_load_and_average_data(opt.cwd, opt.machine,
    #                                                       beam, otype, xing,
    #                                                       error_types, error_loc,
    #                                                       opt.unused_stages), current_params)

    for beam in opt.beams:
        for otype in opt.optic_types:
            for error_types in opt.error_types:
                for error_loc in opt.error_locations:
                    current_params = dict(beam=beam, optic_type=otype, error_types=error_types,
                                          error_loc=error_loc)
                    data = {}
                    ordered = []
                    for xing in opt.xing:
                        id = tripcor.get_nameparts_from_parameters(xing=xing)[0]
                        ordered.append(id)
                        data[id] = _load_and_average_data(opt.cwd, opt.machine,
                                                          beam, otype, xing,
                                                          error_types, error_loc,
                                                          opt.unused_stages)
                    _plot_separate_ampdet(output_folder, data, current_params, ordered,
                                          id="all_xing")


def main_body(opt):
    """ Same stuff for both mains """
    LOG.info("Starting main evaluation loop.")
    opt = tripcor.check_opt(opt)
    output_folder = get_plot_output_folder(opt.cwd)
    # main loop
    for beam, xing, error_types, error_loc in main_loop(opt):
        current_params = dict(beam=beam, xing=xing, error_types=error_types, error_loc=error_loc)
        data = {}
        for otype in opt.optic_types:
            data[otype] = _load_and_average_data(opt.cwd, opt.machine, beam, otype, xing,
                                                 error_types, error_loc, opt.unused_stages)
        yield output_folder, data, current_params


def main_loop(opt):
    """ Main loop over all input variables """
    return ((beam, xing, error_types, error_loc)
            for beam in opt.beams
            for xing in opt.xing
            for error_types in opt.error_types
            for error_loc in opt.error_locations)


# Data Gathering ###############################################################


def _gather_data(cwd, machine, beam, xing, error_types, error_loc, optic_types, seeds, unused_stages):
    """ Gather the data and write it to a file """
    for optic_type in optic_types:

        # ampdet data
        for output_id in _get_all_output_ids(machine, beam, unused_stages):
            seed_data = tfs.TfsDataFrame(
                index=seeds,
                columns=AMPDET_NAMES,
            )
            for seed in seeds:
                output_dir = tripcor.get_output_dir(
                    tripcor.get_seed_dir(cwd, seed), xing, error_types, error_loc, optic_type
                )
                # define seed folder and error definition paths
                seed_data.loc[seed, :] = get_values_from_tfs(
                    get_tfs_name(output_dir, machine, beam, optic_type, output_id))

            title, filename = get_seed_data_title_and_filename(
                beam, xing, error_types, error_loc, optic_type, output_id
            )

            LOG.info("Gathered data for '{:s}'".format(title))
            seed_data.headers["Title"] = title
            seed_data = seed_data.astype(np.float64)
            tfs.write_tfs(
                os.path.join(get_data_output_folder(cwd), filename), seed_data, save_index="SEED"
            )

        # cta data
        seed_data_cta = tfs.TfsDataFrame(
            index=seeds,
            columns=["QX", "QY"]
        )
        for seed in seeds:
            output_dir = tripcor.get_output_dir(
                tripcor.get_seed_dir(cwd, seed), xing, error_types, error_loc, optic_type
            )
            seed_data_cta.loc[seed, :] = get_cta_values(output_dir, beam)

        title, filename = get_cta_seed_data_title_and_filename(
            beam, xing, error_types, error_loc, optic_type)

        LOG.info("Gathered cta data for '{:s}'".format(title))
        seed_data_cta.headers["Title"] = title
        seed_data_cta = seed_data_cta.astype(np.float64)
        tfs.write_tfs(
            os.path.join(get_data_output_folder(cwd), filename), seed_data_cta, save_index="SEED"
        )


def _load_and_average_data(cwd, machine, beam, optic_type, xing, error_types, error_loc, unused_stages):
    """ Load gathered data for a single plot from file """
    df = pandas.DataFrame(
        columns=["{}_{}".format(n, i)
                 for n in AMPDET_NAMES for i in ["AVG", "MIN", "MAX", "STD"]]
    )
    for output_id in _get_all_output_ids(machine, beam, unused_stages):
        _, filename = get_seed_data_title_and_filename(
            beam, xing, error_types, error_loc, optic_type, output_id
        )
        seed_data = tfs.read_tfs(
            os.path.join(get_data_output_folder(cwd), filename), index="SEED"
        )
        label = get_label_from_id(output_id)
        df.loc[label, :] = get_avg_and_error(seed_data)[df.columns].values
    return df


def get_values_from_tfs(tfs_path):
    df = tfs.read_tfs(tfs_path)
    anhx1000 = df.query('NAME == "ANHX" and '
                        'ORDER1 == 1 and ORDER2 == 0')["VALUE"].values[0]
    anhy0100 = df.query('NAME == "ANHY" and ORDER1 == 0 and '
                        'ORDER2 == 1')["VALUE"].values[0]
    anhx0100 = df.query('NAME == "ANHX" and ORDER1 == 0 and '
                        'ORDER2 == 1')["VALUE"].values[0]
    return anhx1000, anhy0100, anhx0100


def get_cta_values(folder, beam):
    cta_file = tripcor_tmplt.TemplateControl.get_cta_names(beam)[1]
    df = tfs.read_tfs(os.path.join(folder, cta_file))
    return df.Q1, df.Q2


def get_avg_and_error(data):
    new_data = pandas.Series()
    for col in data.columns:
        new_data["{}_AVG".format(col)] = np.mean(data.loc[:, col])
        new_data["{}_STD".format(col)] = np.std(data.loc[:, col])
        new_data["{}_MIN".format(col)] = np.min(data.loc[:, col])
        new_data["{}_MAX".format(col)] = np.max(data.loc[:, col])
    return new_data


# Plotting #####################################################################


def _update_min_max(df, current_params):
    d = minmaxdict
    etypes = "".join(current_params["error_types"])
    if etypes not in minmaxdict:
        d[etypes] = {}

    for ampdet in AMPDET_NAMES:
        if ampdet not in d[etypes]:
            d[etypes][ampdet] = dict(min=None, max=None)

        min = np.min(df.loc[:, ampdet + "_AVG"] - df.loc[:, ampdet + "_STD"])
        max = np.max(df.loc[:, ampdet + "_AVG"] + df.loc[:, ampdet + "_STD"])

        if d[etypes][ampdet]["min"] is None or d[etypes][ampdet]["min"] > min:
            d[etypes][ampdet]["min"] = min

        if d[etypes][ampdet]["max"] is None or d[etypes][ampdet]["max"] < max:
            d[etypes][ampdet]["max"] = max


def _plot_separate_ampdet(cwd, data, current_params, line_names, id=None):
    """ Writing separate plots for Ampdet Terms """
    for ampdet in AMPDET_NAMES:
        title = get_plot_title(current_params)
        output_file = os.path.join(cwd, title.replace(" ", ".") + "." + ampdet)
        if id:
            output_file += "." + id
        if title[0] == "b":
            title = "Beam" + title[1:]
        LOG.info("Writing plot for '{:s}'".format(title))

        lines = []

        ps.set_style(PLOT_STYLE, MANUAL_STYLE_NORMAL)
        fig = plt.figure()
        gs = gridspec.GridSpec(1, 1, height_ratios=[1])
        ax = fig.add_subplot(gs[0])
        current_params.update(dict(ampdet=ampdet))
        if "".join(current_params["error_types"]) == "B5A5B6A6":
            add_measurement_lines(ax, current_params, line_names)

        color_cycle = get_colors()
        for line_name in line_names:
            df = data[line_name]  # assumes all df here have the same indices
            current_color = color_cycle.next()
            lines += [go.Scatter(
                x=list(range(len(df.index))),
                y=list(df.loc[:, ampdet + "_AVG"]*1e-4),
                error_y=dict(
                    array=list(df.loc[:, ampdet + "_STD"]*1e-4),
                    color=current_color,
                    opacity=.5,
                ),
                mode='markers+lines',
                name=line_name.replace("_", " "),
                hoverinfo="y+text",
                hovertext=list(df.index),
                line=dict(color=current_color),
            )]

        xaxis = dict(
            range=[-0.1, len(df.index)-0.9],
            # title=title,
            showgrid=True,
            ticks="outer",
            ticktext=list(df.index),
            tickvals=list(range(len(df.index)))
        )

        yaxis = dict(
            title=YLABEL_MAP[ampdet],
        )

        hack_axis(xaxis, yaxis, current_params)
        current_params.pop("ampdet")

        layout = plotly_predef.get_layout(xaxis=xaxis, yaxis=yaxis)
        _plot_and_output(output_file, lines, layout, title, fig)


def _plot_all_ampdets_in_one(cwd, data, current_params):
    """ Plots all ampdet terms into one plot """
    title = get_plot_title(current_params)
    output_file = os.path.join(cwd, title.replace(" ", ".") + ".allampdet")
    if title[0] == "b":
        title = "Beam" + title[1:]

    LOG.info("Writing plot for '{:s}'".format(title))
    lines = []
    color_cycle = ps.get_mpl_color()
    for ampdet in AMPDET_NAMES:
        current_color = color_cycle.next()
        lines += [go.Scatter(
            x=list(range(len(data.index))),
            y=list(data.loc[:, ampdet + "_AVG"]),
            error_y=dict(
                array=list(data.loc[:, ampdet + "_STD"]),
                color=current_color,
                opacity=.5,
            ),
            mode='markers+lines',
            name=ampdet,
            hoverinfo="y+text",
            hovertext=list(data.index),
            line=dict(color=current_color),
        )]

    xaxis = dict(
        range=[-0.1, len(data.index)-0.9],
        title=title,
        showgrid=True,
        ticks="outer",
        ticktext=list(data.index),
        tickvals=list(range(len(data.index)))
    )

    yaxis = dict(
        title="Values  [$m^{-1}$] ",
    )
    layout = plotly_predef.get_layout(xaxis=xaxis, yaxis=yaxis)
    _plot_and_output(output_file, lines, layout, title)


def hist_loop(opt):
    for beam, xing, error_types, error_loc in main_loop(opt):
        for optic_type in opt.optic_types:
            yield beam, xing, error_types, error_loc, optic_type


@entrypoint(get_params(), strict=True)
def make_histogram_plots(opt):
    alpha_mean = .2
    alpha_hist = .6
    title = ""
    ps.set_style('standard')
    opt = tripcor.check_opt(opt)
    cwd = get_data_output_folder(opt.cwd)
    output_folder = get_plot_output_folder(opt.cwd)
    for beam, xing, error_types, error_loc, optic_type in hist_loop(opt):
        fig, axs = plt.subplots(len(AMPDET_NAMES), 1)
        for idx_data, output_id in _ordered_output_ids(opt.machine, beam, opt.unused_stages):
            title, filename = get_seed_data_title_and_filename(
                beam, xing, error_types, error_loc, optic_type, output_id
            )
            seed_df = tfs.read_tfs(os.path.join(cwd, filename), index="SEED")
            y_max = len(seed_df.index)
            for idx_ax, term in enumerate(AMPDET_NAMES):
                ax = axs[idx_ax]
                data = seed_df[term]
                x_pos = data.mean()

                # plot mean
                stem_cont = ax.stem([x_pos], [y_max], markerfmt="", basefmt="", label="_nolegend_")
                plt.setp(stem_cont[1], color=ps.get_mpl_color(idx_data), alpha=alpha_mean)

                # plot std
                # error = data.std()
                # ebar_cont = ax.errorbar(x_pos, y_max, xerr=error, color=ps.get_mpl_color(idx_data),
                #                     label="_nolegend_", marker="")
                # ps.change_ebar_alpha_for_line(ebar_cont, alpha_mean)

                # plot histogram
                data.hist(ax=ax, alpha=alpha_hist, color=ps.get_mpl_color(idx_data), label=output_id)

        for idx_ax, term in enumerate(AMPDET_NAMES):
            axs[idx_ax].set_xlabel(term)
            axs[idx_ax].set_ylabel("Seeds")

        legend = axs[0].legend()
        _reorder_legend(legend, _get_all_output_ids(opt.machine, beam, opt.unused_stages))
        ps.sync2d(axs)
        title = " ".join(title.split(" ")[:-1])
        figfilename = "{:s}.{:s}".format(title.replace(' ', '.'), "histogram")
        fig.canvas.set_window_title(title)
        make_bottom_text(axs[-1], title)
        fig.savefig(os.path.join(output_folder, figfilename + ".pdf"))
        fig.savefig(os.path.join(output_folder, figfilename + ".png"))


@entrypoint(get_params(), strict=True)
def make_histogram2_plots(opt):
    alpha_mean = .2
    alpha_hist = .6
    title = ""
    ps.set_style('standard', MANUAL_STYLE_HIST)
    opt = tripcor.check_opt(opt)
    cwd = get_data_output_folder(opt.cwd)
    output_folder = get_plot_output_folder(opt.cwd)
    for beam, xing, error_types, error_loc, optic_type in hist_loop(opt):
        output = _get_all_output_ids(opt.machine, beam, opt.unused_stages)
        fig, axs = plt.subplots(len(output), 1)
        for idx_ax, output_id in enumerate(output):
            title, filename = get_seed_data_title_and_filename(
                beam, xing, error_types, error_loc, optic_type, output_id
            )
            seed_df = tfs.read_tfs(os.path.join(cwd, filename), index="SEED")
            y_max = len(seed_df.index)
            for idx_data, term in enumerate(AMPDET_NAMES):
                ax = axs[idx_ax]
                data = seed_df[term]
                x_pos = data.mean()

                # plot mean
                stem_cont = ax.stem([x_pos], [y_max], markerfmt="", basefmt="", label="_nolegend_")
                plt.setp(stem_cont[1], color=ps.get_mpl_color(idx_data), alpha=alpha_mean)

                # plot std
                # error = data.std()
                # ebar_cont = ax.errorbar(x_pos, y_max, xerr=error, color=ps.get_mpl_color(idx_data),
                #                     label="_nolegend_", marker="")
                # ps.change_ebar_alpha_for_line(ebar_cont, alpha_mean)

                # plot histogram
                data.hist(ax=ax, alpha=alpha_hist, color=ps.get_mpl_color(idx_data), label=term)

        for idx_ax, output_id in enumerate(output):
            axs[idx_ax].set_ylabel(output_id.replace("_", " "))

        axs[-1].set_xlabel("Value")
        ps.make_top_legend(axs[0], 4)
        ps.sync2d(axs)
        title = " ".join(title.split(" ")[:-1])
        figfilename = "{:s}.{:s}".format(title.replace(' ', '.'), "histogram2")
        fig.canvas.set_window_title(title)
        make_bottom_text(axs[-1], title)
        fig.savefig(os.path.join(output_folder, figfilename + ".pdf"))
        fig.savefig(os.path.join(output_folder, figfilename + ".png"))


def cta_loop(opt):
    return ((beam, error_types, error_loc, optic_type)
            for beam in opt.beams
            for error_types in opt.error_types
            for error_loc in opt.error_locations
            for optic_type in opt.optic_types)


@entrypoint(get_params(), strict=True)
def make_cta_histogram(opt):
    alpha_mean = 1
    alpha_hist = .4
    mod_one = lambda x: np.mod(x, 1)
    ps.set_style('standard', MANUAL_STYLE_CTA)
    opt = tripcor.check_opt(opt)
    cwd = get_data_output_folder(opt.cwd)
    output_folder = get_cta_plot_output_folder(opt.cwd)
    for beam, error_types, error_loc, optic_type in cta_loop(opt):
        fig, ax = plt.subplots(1, 1)
        color_cycle = get_colors()
        for xing in opt.xing:
            color = color_cycle.next()
            _, filename = get_cta_seed_data_title_and_filename(
                beam, xing, error_types, error_loc, optic_type)

            xing_label = tripcor.get_nameparts_from_parameters(xing=xing)[0]
            try:
                xing_label = legend_map[xing_label]
            except KeyError:
                pass

            seed_df = tfs.read_tfs(os.path.join(cwd, filename), index="SEED").apply(mod_one)
            diff = np.abs(seed_df.QX - seed_df.QY) * 1e4

            y_max = len(seed_df.index) / 3

            # plot mean
            x_pos = diff.mean()
            stem_cont = ax.stem([x_pos], [y_max], markerfmt="", basefmt="", label="_nolegend_")
            plt.setp(stem_cont[1], color=color, alpha=alpha_mean, ls="--")

            # plot std
            # error = data.std()
            # ebar_cont = ax.errorbar(x_pos, y_max, xerr=error, color=ps.get_mpl_color(idx_data),
            #                     label="_nolegend_", marker="")
            # ps.change_ebar_alpha_for_line(ebar_cont, alpha_mean)

            # plot histogram
            if diff.std() > 0:
                diff.hist(ax=ax, alpha=alpha_hist, color=color, label="_nolegend_")
                diff.hist(ax=ax, histtype="step", color=color, label=xing_label)

        ax.set_xlabel("|C$^{-}$| [$10^{-4}$]")
        ax.set_ylabel("Count")
        legend = ps.make_top_legend(ax, 2)
        legend.remove()

        figtitle, figfilename = get_cta_plot_title_and_filename(
            beam, error_types, error_loc, optic_type)
        fig.canvas.set_window_title(figtitle)
        fig.tight_layout()
        fig.savefig(os.path.join(output_folder, figfilename + ".hist.pdf"))
        fig.savefig(os.path.join(output_folder, figfilename + ".hist.png"))


# Naming Helper ################################################################


def get_tfs_name(output_dir, machine, beam, optic_type, id):
    id = id.replace(SAME_OPTICS, optic_type)
    if "b{:d}".format(beam) in id and "3030" in id:
        id = tripcor_tmplt.IDS[tripcor_tmplt.STAGE_ORDER[machine][-1]]

    file_name = AMPDET_FILENAME.format(beam=beam, id=id)
    return os.path.join(output_dir, file_name)


def _get_all_output_ids(machine, beam, unused_stages):
    if "CORRECTED" in unused_stages:
        raise EnvironmentError("CORRECTED is not supposed to be filtered by UNUSED_STAGES.")
    out = [tripcor_tmplt.IDS[key] for key in tripcor_tmplt.STAGE_ORDER[machine] if key not in unused_stages]
    if machine == "LHC":
        corrected_by = out[-1] + "_by_b{:d}_{:s}"
        if CORRECTED_BY_OUTPUT:
            out.append(corrected_by.format(tripcor.get_other_beam(beam), SAME_OPTICS))
            out.append(corrected_by.format(beam, DEFAULT_OPTICS))
    return out


def _ordered_output_ids(machine, beam, unused_stages):
    ids = _get_all_output_ids(machine, beam, unused_stages)
    ordered = []
    for stage in PLOT_STAGE_ORDER:
        if stage in ids:
            ordered.append(stage)
        else:
            # mainly for "corrected"
            for id in [id for id in ids if id.startswith(stage)]:
                ordered.append(id)
    return enumerate(ordered)


def get_label_from_id(id):
    return id.replace("_", " ").replace("corrected by", "")


def get_seed_data_title_and_filename(beam, xing, error_types, error_loc, optic_type, output_id):
    parts = tripcor.get_nameparts_from_parameters(beam=beam, optic_type=optic_type, xing=xing,
                error_types=error_types, error_loc=error_loc) + [get_label_from_id(output_id)]

    title = " ".join(parts)
    filename = ".".join(parts + ["seed_data"]) + ".tfs"
    return title, filename


def get_cta_seed_data_title_and_filename(beam, xing, error_types, error_loc, optic_type):
    parts = tripcor.get_nameparts_from_parameters(beam=beam, optic_type=optic_type, xing=xing,
                  error_types=error_types, error_loc=error_loc)
    title = " ".join(parts)
    filename = ".".join(parts + ["cta_seed_data"]) + ".tfs"
    return title, filename


def get_cta_plot_title_and_filename(beam, error_types, error_loc, optic_type):
    parts = tripcor.get_nameparts_from_parameters(beam=beam, optic_type=optic_type,
                                                  error_types=error_types, error_loc=error_loc)
    title = " ".join(parts)
    filename = ".".join(parts + ["cta"])
    return title, filename


def get_cta_plot_output_folder(cwd):
    path = os.path.join(get_plot_output_folder(cwd), "cta_hist")
    iotools.create_dirs(path)
    return path


def get_plot_output_folder(cwd):
    path = os.path.join(cwd, "results_plot")
    iotools.create_dirs(path)
    return path


def get_data_output_folder(cwd):
    path = os.path.join(cwd, "results_gathered")
    iotools.create_dirs(path)
    return path


def _reorder_legend(leg, ordered_labels):
    ax = leg.axes
    handles, labels = ax.get_legend_handles_labels()
    sorting = [labels.index(l) for l in ordered_labels]
    new_handles = np.array(handles)[sorting].tolist()
    ps.make_top_legend(ax, 4, new_handles, ordered_labels)


def make_bottom_text(ax, text):
    xlim = ax.get_xlim()
    xpos = xlim[0] + (xlim[1] - xlim[0]) * .5

    axtr = ax.transData.inverted()  # Display -> Axes
    figtr = ax.get_figure().transFigure  # Figure -> Display
    ypos = axtr.transform(figtr.transform([0, 0.001]))[1]
    ax.text(xpos, ypos, text, ha='center')


def _plot_and_output(path, data, layout, title, fig=None):
    ps.set_style(PLOT_STYLE, MANUAL_STYLE_NORMAL)
    fig = mpl_wrap.plot_wrapper(data, layout, title, LEGEND_COLS, fig)
    fig.tight_layout()
    with open(path + ".json", "w") as f:
        f.write(json.dumps({'data': data, 'layout': layout}))
    fig.savefig(path + ".png")
    fig.savefig(path + ".pdf")
    # mpdf = PdfPages(path + ".pdf")
    # mpdf.savefig(figure=fig, bbox_inches='tight')
    # mpdf.close()


def get_plot_title(current_params):
    title = " ".join(tripcor.get_nameparts_from_parameters(**current_params)).replace("_", " ")
    return title


def copy_to_pres(src, dst):
    for file in os.listdir(src):
        if file.endswith(".pdf"):
            shutil.copy(
                os.path.join(src, file),
                os.path.join(dst, file),
            )

# Script Mode ##################################################################


if __name__ == '__main__':
    # plot_crossing_oneplot(entry_cfg="./irnl18_triplet_correction_configs/md3311.ini", section="ForTest")

    # gather_all_data(entry_cfg="./irnl18_triplet_correction_configs/md3311.ini", section="ForPlot")
    # gather_all_data(entry_cfg="./irnl18_triplet_correction_configs/md3311.ini", section="CrossingIP5")
    # gather_all_data(entry_cfg="./irnl18_triplet_correction_configs/md3311.ini", section="NotCrossingIP5")

    plot_crossing_oneplot(entry_cfg="./irnl18_triplet_correction_configs/md3311.ini", section="ForPlot")
    # make_cta_histogram(entry_cfg="./irnl18_triplet_correction_configs/md3311.ini", section="ForPlot")
    # plt.show()
    # copy_to_pres(get_cta_plot_output_folder("/home/jdilly/link_afs_work/private/STUDY.18.LHC.MD3311"),
    #              "/media/jdilly/Storage/Projects/NOTE.18.MD3311.Amplitude_Detuning/results.md_note/results/simulation/cta_hist")
    #
    copy_to_pres("/home/jdilly/link_afs_work/private/STUDY.18.LHC.MD3311/results_plot",
                 "/media/jdilly/Storage/Projects/NOTE.18.MD3311.Amplitude_Detuning/results.md_note/results/simulation")
    # main(entry_cfg="./irnl18_triplet_correction_configs/md3311.ini", section="CrossingIP5")
    # main(entry_cfg="./irnl18_triplet_correction_configs/md3311.ini", section="CrossingIP1")
    # load_and_plot_all_saved(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingOnOff")
    # make_histogram2_plots(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingOnOff")
    # make_histogram_plots(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingOnOff")

    # main(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingIP1")
    # load_and_plot_all_saved(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingIP1")
    # make_histogram2_plots(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingIP1")
    #
    # main(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingIP5")
    # load_and_plot_all_saved(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingIP5")
    # make_histogram2_plots(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingIP5")

    # main(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrors")
    # load_and_plot_all_saved(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrors")
    # make_histogram2_plots(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrors")
    # make_histogram_plots(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrors")


    # main_terms_oneplot(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrorsXingTest")
    # load_and_plot_all_saved(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrorsXingTest")
    # make_histogram2_plots(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrorsXingTest")

    # main(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="OnlySextupoles")
    # load_and_plot_all_saved(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="OnlySextupoles")
    # make_histogram_plots(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="OnlySextupoles")
    #
    # main(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="OnlyHighpoles")
    # load_and_plot_all_saved(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="OnlyHighpoles")
    # make_histogram_plots(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="OnlyHighpoles")
    #
    # main(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrorsXing255")
    # load_and_plot_all_saved(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrorsXing255")
    # make_histogram_plots(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrorsXing255")
    #
    # main(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrorsOffDisp")
    # load_and_plot_all_saved(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrorsOffDisp")
    # make_histogram_plots(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrorsOffDisp")
