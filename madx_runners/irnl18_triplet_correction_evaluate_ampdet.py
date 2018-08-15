import os
import sys

import numpy as np
import pandas
import enlighten

# Beta-Beat Repo imports
beta_beta_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.append(beta_beta_path)

from utils.entrypoint import entrypoint
from utils import logging_tools
import irnl18_triplet_correction as tripcor
import irnl18_triplet_correction_template_control as tripcor_tmplt
from tfs_files import tfs_pandas as tfs


LOG = logging_tools.get_logger(__name__)


AMPDET_FILENAME = "ptc_normal.ampdet.{id:s}.dat"  # see madx_snippets.py
AMPDET_NAMES = ["ANHX1000", "ANHY0100", "ANHX0100"]

@entrypoint(tripcor.get_params(), strict=True)
def main(opt):
    """ Main loop over all input variables """
    LOG.info("Starting main evaluation loop.")
    # setup progress bar:
    prog_man = enlighten.get_manager()
    prog_bar = prog_man.counter(
        total=tripcor.get_number_of_jobs(opt)[0]/len(opt.seeds),
        desc="Plots: ",
    )
   # main loop
    for beam in opt.beams:
        for xing in opt.xing:
            for error_types in opt.error_types:
                for error_loc in opt.error_locations:
                    data = gather_plot_data(opt.cwd, beam, xing, error_types, error_loc,
                                            opt.optic_types, opt.seeds)

                    prog_bar.update()
    prog_man.stop()


# Data Gathering ###############################################################


def gather_plot_data(cwd, beam, xing, error_types, error_loc, optic_types, seeds):
    """ Gather the data for a single plot """
    data = {}
    for optic_type in optic_types:
        ids = _get_all_output_ids(beam, optic_type)
        data[optic_type] = pandas.DataFrame(
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
                    get_tfs_name(cwd, seed, xing, error_types,
                                 error_loc, optic_type, output_id
                                 )
                )
            data[optic_type].loc[output_id, :] = get_avg_and_error(seed_data).to_frame().T
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
    for col in data.cloumns:
        new_data["{}_AVG".format(col)] = np.mean(data.loc[:, col])
        new_data["{}_STD".format(col)] = np.std(data.loc[:, col])
        new_data["{}_MIN".format(col)] = np.min(data.loc[:, col])
        new_data["{}_MAX".format(col)] = np.max(data.loc[:, col])
    return new_data


# Plotting #####################################################################


def plot_data(data):



# Naming Helper ################################################################


def get_tfs_name(cwd, seed, xing, error_types, error_loc, optic_type, id):
    output_dir = tripcor.get_output_dir(
        tripcor.get_seed_dir(cwd, seed), xing, error_types, error_loc, optic_type
    )
    file_name = AMPDET_FILENAME.format(id=id)
    return os.path.join(output_dir, file_name)


def _get_all_output_ids(beam, optic_type):
    out = [tripcor_tmplt.IDS[key] for key in tripcor_tmplt.STAGE_ORDER]
    corrected_by = out[-1] + "_by_b{:d}_{:s}"
    out.append(corrected_by.format(tripcor.get_other_beam(beam), optic_type))
    if optic_type != "3030":
        out.append(corrected_by.format(beam, "3030"))
    return out


# Script Mode ##################################################################


if __name__ == '__main__':
    # main()
    main(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="Beam2_wXing")
