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
from utils.plotting import plot_style as ps
import irnl18_triplet_correction as tripcor
import irnl18_triplet_correction_template_control as tripcor_tmplt
from tfs_files import tfs_pandas as tfs
import udillyties.plotly_helpers.predefined as plotly_predef


LOG = logging_tools.get_logger(__name__)


AMPDET_FILENAME = "ptc_normal.ampdet.b{beam:d}.{id:s}.dat"  # see madx_snippets.py
AMPDET_NAMES = ["ANHX1000", "ANHY0100", "ANHX0100"]
UNUSED_STAGES = ["ARCAPPLIED"]  # see in template_control


def get_params():
    """ Same params as in the creation of the files """
    return tripcor.get_params()


@entrypoint(get_params(), strict=True)
def main(opt):
    """ Main loop over all input variables """
    LOG.info("Starting main evaluation loop.")
    output_folder = get_output_folder(opt.cwd)

    prog_man, prog_bar = setup_progress_bar(tripcor.get_number_of_jobs(opt)[0]/len(opt.seeds))

    # main loop
    for beam, xing, error_types, error_loc in main_loop(opt):
                    data = gather_plot_data(opt.cwd, beam, xing, error_types, error_loc,
                                            opt.optic_types, opt.seeds)

                    title = get_plot_title(beam, xing, error_types, error_loc)

                    save_plot_data(output_folder, data, title, opt.optic_types)

                    prog_bar.update()
    prog_man.stop()


def main_loop(opt):
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


def gather_plot_data(cwd, beam, xing, error_types, error_loc, optic_types, seeds):
    """ Gather the data for a single plot """
    data = {}
    for optic_type in optic_types:
        ids = _get_all_output_ids(beam, optic_type)
        df = pandas.DataFrame(
            index=ids,
            columns=["{}_{}".format(n, i)
                     for n in AMPDET_NAMES for i in ["AVG", "MIN", "MAX", "STD"]]
        )
        for output_id in ids:
            seed_data = pandas.DataFrame(
                index=seeds,
                columns=AMPDET_NAMES,
            )
            for seed in seeds:
                # define seed folder and error definition paths
                seed_data.loc[seed, :] = get_values_from_tfs(
                    get_tfs_name(cwd, beam, seed, xing, error_types,
                                 error_loc, optic_type, output_id
                                 )
                )

            df.loc[output_id, :] = get_avg_and_error(seed_data)[df.columns].values
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
        x_names = []
        color_cycle = ps.get_mpl_color()
        for line_name in line_names:
            df = data[line_name]
            x_names = x_names + [i for i in df.index if i not in x_names]
            current_color = color_cycle.next()
            lines += [go.Scatter(
                x=list(range(len(df.index))),
                y=list(df.loc[:, ampdet + "_AVG"]),
                error_y =dict(
                    array=list(df.loc[:, ampdet + "_STD"]),
                    color=current_color,
                ),
                mode='markers+lines',
                name=line_name,
                hoverinfo="y+text",
                hovertext=list(df.index),
                line=dict(color=current_color),
            )]

        xaxis = dict(
            range=[-0.1, len(x_names)],
            title=full_title,
            showgrid=True,
            ticks="outer",
            ticktext=x_names,
            tickvals=list(range(len(x_names)))
        )

        yaxis = dict(
            title=ampdet,
        )
        layout = plotly_predef.get_layout(xaxis=xaxis, yaxis=yaxis)

        output_file = os.path.join(cwd, full_title.replace(" ", ".") + ".json")
        with open(output_file, "w") as f:
            f.write(json.dumps({'data': lines, 'layout': layout}))


# Naming Helper ################################################################


def get_tfs_name(cwd, beam, seed, xing, error_types, error_loc, optic_type, id):
    output_dir = tripcor.get_output_dir(
        tripcor.get_seed_dir(cwd, seed), xing, error_types, error_loc, optic_type
    )
    file_name = AMPDET_FILENAME.format(beam=beam, id=id)
    return os.path.join(output_dir, file_name)


def get_plot_title(beam, xing, error_types, error_loc):
    # xing
    xing_map = {
        True: "wXing",
        False: "noXing",
        "else": "{:s}Xing",
    }
    try:
        xing_str = xing_map[xing]
    except KeyError:
        xing_str = xing_map["else"].format(xing)

    # error_types
    error_type_str = "errors {:s}".format(" ".join(error_types))

    # error_loc
    error_loc_str = "in all IPs" if "ALL" == error_loc else "in {:s}".format(error_loc)

    return " ".join(["B{:d}".format(beam), xing_str,error_type_str, error_loc_str])


def _get_all_output_ids(beam, optic_type):
    out = [tripcor_tmplt.IDS[key] for key in tripcor_tmplt.STAGE_ORDER if key not in UNUSED_STAGES]
    corrected_by = out[-1] + "_by_b{:d}_{:s}"
    out.append(corrected_by.format(tripcor.get_other_beam(beam), optic_type))
    if optic_type != "3030":
        out.append(corrected_by.format(beam, "3030"))
    return out


def get_output_folder(cwd):
    path = os.path.join(cwd, "plot_output")
    iotools.create_dirs(path)
    return path


# Script Mode ##################################################################


if __name__ == '__main__':
    # main()
    main(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingOnOff")
