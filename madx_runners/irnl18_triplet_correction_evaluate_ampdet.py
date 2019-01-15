import os
import sys

import enlighten
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
from matplotlib import pyplot as plt


LOG = logging_tools.get_logger(__name__)


AMPDET_FILENAME = "ptc_normal.ampdet.b{beam:d}.{id:s}.dat"  # see madx_snippets.py
AMPDET_NAMES = ["ANHX1000", "ANHY0100", "ANHX0100"]
SAME_OPTICS = "same_optics"  # identifyier to be replaced by optics in filename
DEFAULT_OPTICS = "3030"  # optics to compare the correction by

# plotting order so histograms look nice
PLOT_STAGE_ORDER = ["errors_all", "errors_ip", "errors_mqx", "errors_mb_ip", "corrected", "errors_arc", "nominal"]


def get_params():
    """ Same params as in the creation of the files """
    return tripcor.get_params()


@entrypoint(get_params(), strict=True)
def main(opt):
    """ Main function for separate plots for ampdet terms """
    for output_folder, data, title in main_body(opt):
        save_plot_data(output_folder, data, title, opt.optic_types)


@entrypoint(get_params(), strict=True)
def main_terms_oneplot(opt):
    if len(opt.optic_types) > 1:
        raise ValueError("This method runs only with one line")
    """ Main function for separate plots for optic types """
    for output_folder, data, title in main_body(opt):
        save_plot_data_terms_oneplot(output_folder, data, title, opt.optic_types[0])


def main_body(opt):
    """ Same stuff for both mains """
    LOG.info("Starting main evaluation loop.")
    opt = tripcor.check_opt(opt)
    output_folder = get_output_folder(opt.cwd)
    # main loop
    for beam, xing, error_types, error_loc in main_loop(opt):
        data = gather_plot_data(opt.cwd, opt.machine, beam, xing, error_types, error_loc,
                                opt.optic_types, opt.seeds, opt.unused_stages)

        title = " ".join(p.replace("_", " ") for p in
                         tripcor.get_nameparts_from_parameters(
                             beam=beam, xing=xing, error_types=error_types, error_loc=error_loc))
        yield output_folder, data, title


def main_loop(opt):
    """ Main loop over all input variables """
    return ((beam, xing, error_types, error_loc)
            for beam in opt.beams
            for xing in opt.xing
            for error_types in opt.error_types
            for error_loc in opt.error_locations)


def setup_progress_bar(length):
    prog_man = enlighten.get_manager()
    prog_bar = prog_man.counter(
        total=length,
        desc="Plots: ",
    )
    return prog_man, prog_bar


# Data Gathering ###############################################################


def gather_plot_data(cwd, machine, beam, xing, error_types, error_loc, optic_types, seeds, unused_stages):
    """ Gather the data for a single plot """
    data = {}
    for optic_type in optic_types:
        df = pandas.DataFrame(
            columns=["{}_{}".format(n, i)
                     for n in AMPDET_NAMES for i in ["AVG", "MIN", "MAX", "STD"]]
        )
        for output_id in _get_all_output_ids(machine, beam, unused_stages):
            seed_data = tfs.TfsDataFrame(
                index=seeds,
                columns=AMPDET_NAMES,
            )
            for seed in seeds:
                # define seed folder and error definition paths
                seed_data.loc[seed, :] = get_values_from_tfs(
                    get_tfs_name(cwd, machine, beam, seed, xing, error_types,
                                 error_loc, optic_type, output_id
                                 )
                )

            label = get_label_from_id(output_id)
            title, filename = get_seed_data_title_and_filename(
                beam, xing, error_types, error_loc, optic_type, output_id
            )
            seed_data.headers["Title"] = title
            seed_data = seed_data.astype(np.float64)
            tfs.write_tfs(
                os.path.join(get_output_folder(cwd), filename), seed_data, save_index="SEED"
            )
            df.loc[label, :] = get_avg_and_error(seed_data)[df.columns].values
        data[optic_type] = df
    return data


def get_values_from_tfs(tfs_path):
    df = tfs.read_tfs(tfs_path)
    anhx1000 = df.query('NAME == "ANHX" and '
                        'ORDER1 == 1 and ORDER2 == 0')["VALUE"].values[0]
    anhy0100 = df.query('NAME == "ANHY" and ORDER1 == 0 and '
                        'ORDER2 == 1')["VALUE"].values[0]
    anhx0100 = df.query('NAME == "ANHX" and ORDER1 == 0 and '
                        'ORDER2 == 1')["VALUE"].values[0]
    return anhx1000, anhy0100, anhx0100


def get_avg_and_error(data):
    new_data = pandas.Series()
    for col in data.columns:
        new_data["{}_AVG".format(col)] = np.mean(data.loc[:, col])
        new_data["{}_STD".format(col)] = np.std(data.loc[:, col])
        new_data["{}_MIN".format(col)] = np.min(data.loc[:, col])
        new_data["{}_MAX".format(col)] = np.max(data.loc[:, col])
    return new_data


# Plotting #####################################################################


def save_plot_data(cwd, data, title, line_names):
    for ampdet in AMPDET_NAMES:
        full_title = "{} {}".format(title, ampdet)
        LOG.info("Writing plot for '{:s}'".format(full_title))

        lines = []
        color_cycle = ps.get_mpl_color()
        for line_name in line_names:
            df = data[line_name]  # assumes all df here have the same indices
            current_color = color_cycle.next()
            lines += [go.Scatter(
                x=list(range(len(df.index))),
                y=list(df.loc[:, ampdet + "_AVG"]),
                error_y=dict(
                    array=list(df.loc[:, ampdet + "_STD"]),
                    color=current_color,
                    opacity=.5,
                ),
                mode='markers+lines',
                name=line_name,
                hoverinfo="y+text",
                hovertext=list(df.index),
                line=dict(color=current_color),
            )]

        xaxis = dict(
            range=[-0.1, len(df.index)-0.9],
            title=full_title,
            showgrid=True,
            ticks="outer",
            ticktext=list(df.index),
            tickvals=list(range(len(df.index)))
        )

        yaxis = dict(
            title=ampdet,
        )
        layout = plotly_predef.get_layout(xaxis=xaxis, yaxis=yaxis)

        output_file = os.path.join(cwd, full_title.replace(" ", ".") + ".json")
        with open(output_file, "w") as f:
            f.write(json.dumps({'data': lines, 'layout': layout}))


def save_plot_data_terms_oneplot(cwd, data, title, line_name):
    title = title.split()
    title.insert(1, line_name)
    title = " ".join(title)

    LOG.info("Writing plot for '{:s}'".format(title))
    lines = []
    color_cycle = ps.get_mpl_color()
    for ampdet in AMPDET_NAMES:
        df = data[line_name]
        current_color = color_cycle.next()
        lines += [go.Scatter(
            x=list(range(len(df.index))),
            y=list(df.loc[:, ampdet + "_AVG"]),
            error_y=dict(
                array=list(df.loc[:, ampdet + "_STD"]),
                color=current_color,
                opacity=.5,
            ),
            mode='markers+lines',
            name=ampdet,
            hoverinfo="y+text",
            hovertext=list(df.index),
            line=dict(color=current_color),
        )]

    xaxis = dict(
        range=[-0.1, len(df.index)-0.9],
        title=title,
        showgrid=True,
        ticks="outer",
        ticktext=list(df.index),
        tickvals=list(range(len(df.index)))
    )

    yaxis = dict(
        title="Values",
    )
    layout = plotly_predef.get_layout(xaxis=xaxis, yaxis=yaxis)

    output_file = os.path.join(cwd, (title).replace(" ", ".") + ".json")
    with open(output_file, "w") as f:
        f.write(json.dumps({'data': lines, 'layout': layout}))


@entrypoint(get_params(), strict=True)
def load_and_plot_all_saved(opt):
    ps.set_style("standard", {u'grid.linestyle': u'--', u'errorbar.capsize': 2})
    opt = tripcor.check_opt(opt)
    cwd = get_output_folder(opt.cwd)
    for file in os.listdir(cwd):
        if file.endswith(".json"):
            file = os.path.join(cwd, file)
            fig = mpl_wrap.plot_from_json(file)
            fig.savefig(file.replace(".json", ".png"))
            fig.savefig(file.replace(".json", ".pdf"))


@entrypoint(get_params(), strict=True)
def make_histogram_plots(opt):
    def loop(opt):
        for beam, xing, error_types, error_loc in main_loop(opt):
            for optic_type in opt.optic_types:
                yield beam, xing, error_types, error_loc, optic_type

    alpha_mean = .2
    alpha_hist = .6
    title = ""
    ps.set_style('standard')
    opt = tripcor.check_opt(opt)
    cwd = get_output_folder(opt.cwd)
    for beam, xing, error_types, error_loc, optic_type in loop(opt):
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
        fig.savefig(os.path.join(cwd, figfilename + ".pdf"))
        fig.savefig(os.path.join(cwd, figfilename + ".png"))

@entrypoint(get_params(), strict=True)
def make_histogram2_plots(opt):
    def loop(opt):
        for beam, xing, error_types, error_loc in main_loop(opt):
            for optic_type in opt.optic_types:
                yield beam, xing, error_types, error_loc, optic_type

    alpha_mean = .2
    alpha_hist = .6
    title = ""
    ps.set_style('standard')
    opt = tripcor.check_opt(opt)
    cwd = get_output_folder(opt.cwd)
    for beam, xing, error_types, error_loc, optic_type in loop(opt):
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
        fig.savefig(os.path.join(cwd, figfilename + ".pdf"))
        fig.savefig(os.path.join(cwd, figfilename + ".png"))

# Naming Helper ################################################################


def get_tfs_name(cwd, machine, beam, seed, xing, error_types, error_loc, optic_type, id):
    output_dir = tripcor.get_output_dir(
        tripcor.get_seed_dir(cwd, seed), xing, error_types, error_loc, optic_type
    )
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
        corrected_by = out[-1] + " _by_b{:d}_{:s}"
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
    return id.replace("_", " ").replace("corrected by", "t by")


def get_seed_data_title_and_filename(beam, xing, error_types, error_loc, optic_type, output_id):
    parts = tripcor.get_nameparts_from_parameters(beam=beam, optic_type=optic_type, xing=xing,
                error_types=error_types, error_loc=error_loc) + [get_label_from_id(output_id)]

    title = " ".join(parts)
    filename = ".".join(parts + ["seed_data"]) + ".tfs"
    return title, filename


def get_output_folder(cwd):
    path = os.path.join(cwd, "results_plot")
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
    ypos = axtr.transform(figtr.transform([0, 0.004]))[1]
    ax.text(xpos, ypos, text, ha='center')
    ax.get_figure().tight_layout()



# Script Mode ##################################################################


if __name__ == '__main__':
    # main(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingOnOff")
    # load_and_plot_all_saved(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingOnOff")
    #
    # main(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingIP1")
    # load_and_plot_all_saved(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingIP1")
    #
    # main(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingIP5")
    # load_and_plot_all_saved(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingIP5")

    # main(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrors")
    # load_and_plot_all_saved(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrors")
    # make_histogram2_plots(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrors")
    # make_histogram_plots(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrors")


    main_terms_oneplot(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrorsXingTest")
    load_and_plot_all_saved(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrorsXingTest")
    make_histogram2_plots(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrorsXingTest")

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
