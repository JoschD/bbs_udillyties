"""
This script compares all available corrections (27.04.2018) with each other and plots them
via check_calculated_corrections.py

To get plotly results you might want to hijack this by importing the plotly_helpers/plot_tfs.py
in there (produces json files that can be loaded directly for plotting).

You need to have the analysed data at hand, i.e. get_llm data (see DATA_DIR)

Also replace occurences of the model-folder path in the job.***.madx files with %(THISDIR)s and
rename those files to template.***.madx
"""


import os
import sys
import shutil

import matplotlib
matplotlib.use('pgf')

BETA_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
sys.path.append(BETA_ROOT)
from utils import logging_tools, iotools
from global_correct_iterative import global_correction
from generate_fullresponse_pandas import create_response
import check_calculated_corrections
from correction import correct, correct_coupleDy
from correction.fullresponse import generateFullResponse_parallel


LOG = logging_tools.get_logger(__name__)

ACCEL = "lhc"
ACCELMODE = "lhc_runII_2018"

DATA_DIR = {
    1: {
        "normal": "/media/jdilly/Storage/Projects/2018_03_correction_comparison_to_correct.py/21_Data_for_latex/b1_data/data_for_normal",
        "coupling": "/media/jdilly/Storage/Projects/2018_03_correction_comparison_to_correct.py/21_Data_for_latex/b1_data/data_for_coupling",
},
    2: {
        "normal": "/media/jdilly/Storage/Projects/2018_03_correction_comparison_to_correct.py/21_Data_for_latex/b2_data/data_for_normal",
        "coupling": "/media/jdilly/Storage/Projects/2018_03_correction_comparison_to_correct.py/21_Data_for_latex/b2_data/data_for_coupling",
},
}

MODEL_DIR = {
    1: "/media/jdilly/Storage/Projects/2018_03_correction_comparison_to_correct.py/21_Data_for_latex/b1_data/b1_with_newTunes",
    2: "/media/jdilly/Storage/Projects/2018_03_correction_comparison_to_correct.py/21_Data_for_latex/b2_data/30cm_all_knobs_in",
}

CORRECTIONS_SUBDIR = "Corrections"

DELTA_K = 2e-5

VARIABLES = {
    "normal": ["MQM", "MQT", "MQTL", "MQY"],
    "coupling": ["coupling_knobs"],
}

RESPONSES = {
    "madx": "Fullresponse_madx",
    "twiss": "Fullresponse_twiss",
}

ERROR_CUTS = {
    1: {
        "normal": [0.035, 0.035, 0.01, 0.01, 0.2, 0.027],
        "coupling": [0.025, 0.025, 0.025, 0.025, 0.0],
       },
    2: {
        "normal": [0.035, 0.035, 0.01, 0.01, 0.2, 0.027],
        "coupling": [0.25, 0.25, 0.25, 0.25, 0.0],
    },
}

MODEL_CUTS = {
    1: {
        "normal": [0.25, 0.25, 0.02, 0.02, 0.5, 0.1],
        "coupling": [0., 0., 0., 0., 0.0],
       },
    2: {
        "normal": [0.25, 0.25, 0.02, 0.02, 0.5, 0.1],
        "coupling": [0., 0., 0., 0., 0.0],
    },
}

PARAMS = {
    "normal": ["BBX", "BBY", "MUX", "MUY", "NDX", "Q"],
    "coupling": ["F1001R", "F1001I", "F1010R", "F1010I", "DY"],
}

BETA_FILE = "getbeta"


# Main Callers ###############################################################


def correct_iter_all_normal(beam, method, iter):
    correct_iterative(
        method=method,
        mode="normal",
        weights=[1., 1., 1., 1., 1., 10.],
        beam=beam,
        iter=iter,
    )


def correct_iter_NDX(beam, method, iter):
    correct_iterative(
        method=method,
        mode="normal",
        weights=[0., 0., 0., 0., 1., 0.],
        beam=beam,
        iter=iter,
    )


def correct_iter_BB_NDX(beam, method, iter):
    correct_iterative(
        method=method,
        mode="normal",
        weights=[1., 1., 0., 0., 1., 0.],
        beam=beam,
        iter=iter,
    )


def correct_iter_BBX_BBY_MUX_MUY_Q(beam, method, iter):
    correct_iterative(
        method=method,
        mode="normal",
        weights=[1., 1., 1., 1., 0., 10.],
        beam=beam,
        iter=iter,
    )


def correct_iter_all_coupling(beam, method, iter):
    correct_iterative(
        method=method,
        mode="coupling",
        weights=[1., 1., 1., 1., 1.],
        beam=beam,
        iter=iter,
    )


def correct_iter_sum_diff_coupling(beam, method, iter):
    correct_iterative(
        method=method,
        mode="coupling",
        weights=[1., 1., 1., 1., 0.],
        beam=beam,
        iter=iter,
    )


def correct_iter_sum_coupling(beam, method, iter):
    correct_iterative(
        method=method,
        mode="coupling",
        weights=[1., 1., 0., 0., 0.],
        beam=beam,
        iter=iter,
    )


def correct_old_all_coupling(beam):
    correct_old(
        mode="coupling",
        weights=[1, 1, 1, 1, 1],
        beam=beam,
    )


def correct_old_sum_diff_coupling(beam):
    correct_old(
        mode="coupling",
        weights=[1, 1, 1, 1, 0],
        beam=beam,
    )


def correct_old_sum_coupling(beam):
    correct_old(
        mode="coupling",
        weights=[1, 1, 0, 0, 0],
        beam=beam,
    )


def correct_old_all_normal(beam):
    correct_old(
        mode="normal",
        weights=[1, 1, 1, 1, 1, 10],
        beam=beam,
    )


def correct_old_NDX(beam):
    correct_old(
        mode="normal",
        weights=[0, 0, 0, 0, 1, 0],
        beam=beam,
    )


def correct_old_BB_NDX(beam):
    correct_old(
        mode="normal",
        weights=[0, 0, 1, 1, 1, 0],
        beam=beam,
    )


def correct_old_BBX_BBY_MUX_MUY_Q(beam):
    correct_old(
        mode="normal",
        weights=[1, 1, 1, 1, 0, 10],
        beam=beam,
    )


# Actual Functionality #######################################################


def prepare_model(beam):
    """ Update model paths for madx """
    folder = MODEL_DIR[beam]
    for f in os.listdir(MODEL_DIR[beam]):
        if f.startswith("template."):
            full_temp = os.path.join(folder, f)
            full_job = os.path.join(folder, f.replace("template.", "job."))
            with open(full_temp, "r") as template:
                content = template.read()
            with open(full_job, "w") as job:
                job.write(content % {"THISFOLDER": folder})


def create_responses(beam):
    """ Create responses to be used (saved in DATA-DIR!)"""
    for mode in ["normal", "coupling"]:
        f_madx = os.path.join(DATA_DIR[beam][mode], RESPONSES["madx"])
        f_twiss = os.path.join(DATA_DIR[beam][mode], RESPONSES["twiss"])

        args = {
            "accel": "lhc",
            "lhc_mode": "lhc_runII_2018",
            "beam": beam,
            "delta_k": DELTA_K,
            "variable_categories": VARIABLES[mode],
            "model_dir": MODEL_DIR[beam],
            "debug": False,
        }

        args_madx = args.copy()
        args_madx.update({"creator": "madx", "outfile_path": f_madx})
        create_response(**args_madx)

        args_twiss = args.copy()
        args_twiss.update({"creator": "twiss", "outfile_path": f_twiss})
        create_response(**args_twiss)


def correct_iterative(method, mode, weights, beam, iter=0):
    """ Use global_correction for iterative correction

    Args:
        method: twiss or madx
        mode: normal or coupling
        weights: weights to use on parameters
        beam: 1 or 2
        iter: number of reiterations
    """
    temp_dir = os.path.join(DATA_DIR[beam][mode],
                            "temp_correct_B{:d}_{:s}_{:s}_iter{:d}".format(
                                beam,
                                method,
                                "_".join(p for w, p in zip(weights, PARAMS[mode]) if w != 0),
                                iter,
                            )
                            )
    fullresponse = os.path.join(DATA_DIR[beam][mode], RESPONSES[method])

    global_correction(
        accel=ACCEL,
        lhc_mode=ACCELMODE,
        beam=beam,
        fullresponse_path=fullresponse,
        meas_dir=DATA_DIR[beam][mode],
        model_dir=MODEL_DIR[beam],
        output_path=temp_dir,
        svd_cut=0.01,
        errorcut=ERROR_CUTS[beam][mode],
        modelcut=MODEL_CUTS[beam][mode],
        optics_params=PARAMS[mode],
        weights=weights,
        use_errorbars=False,
        variable_categories=VARIABLES[mode],
        beta_file_name=BETA_FILE,
        max_iter=iter,
        debug=False,
    )

    correction_dir = os.path.join(DATA_DIR[beam][mode],
                                  CORRECTIONS_SUBDIR,
                                  "B{:d}_{:s}".format(
                                      beam,
                                      "_".join(p for w, p in zip(weights, PARAMS[mode]) if w != 0),
                                  ),
                                  "{:s}_iter{:d}".format(method, iter))
    _copy_corrections(temp_dir, correction_dir, "_iter")


def create_old_responses(beam):
    """ Create responses for the old correction """
    sys.argv = [
        "python",
        "generateFullResponse_parallel.py",
        "--accel", "LHCB{:d}".format(beam),
        "--path", MODEL_DIR[beam],
        "--core", os.path.join(BETA_ROOT, "correction", "fullresponse"),
        "--deltak",   str(DELTA_K),
        "--deltakl", "0.0",
        "-t"
    ]
    generateFullResponse_parallel._start()


def correct_old(mode, weights, beam):
    """ Use the old correction method to correct for either normal or coupling

    Args:
        mode: normal or coupling
        weights: weigths to use on the parameter
        beam: 1 or 2
    """
    if mode == "normal":
        sys.argv = [
            "python",
            "correct.py",
            "--accel", "LHCB{:d}".format(beam),
            "--tech", "SVD",
            "--ncorr", "5",
            "--weight", ",".join(["{:d}".format(int(w)) for w in weights]),
            "--path", DATA_DIR[beam][mode],
            "--cut", "0.01",
            "--errorcut", ",".join([str(ERROR_CUTS[beam][mode][i]) for i in [0, 1, 5]]),
            "--modelcut", ",".join([str(MODEL_CUTS[beam][mode][i]) for i in [0, 1, 5]]),
            "--opt", MODEL_DIR[beam],
            "--betafile", BETA_FILE,
            "--rpath", BETA_ROOT,
            "--MinStr", str(DELTA_K),
            "--Variables", ",".join(VARIABLES[mode]),
            "--errweight", "0",
        ]
        correct._start()
    else:
        sys.argv = [
            "python",
            "correct_coupleDy.py",
            "--accel", "LHCB{:d}".format(beam),
            "--Dy", ",".join(["{:d}".format(int(w)) for w in weights]),
            "--path", DATA_DIR[beam][mode],
            "--cut", "0.01",
            "--errorcut", ",".join([str(ERROR_CUTS[beam][mode][i]) for i in [0, 4]]),
            "--modelcut", ",".join([str(MODEL_CUTS[beam][mode][i]) for i in [0, 4]]),
            "--opt", MODEL_DIR[beam],
            "--rpath", BETA_ROOT,
            "--MinStr", str(DELTA_K),
            "--Variables", ",".join(VARIABLES[mode]),
        ]
        correct_coupleDy._start()

    correction_dir = os.path.join(DATA_DIR[beam][mode],
                                  CORRECTIONS_SUBDIR,
                                  "B{:d}_{:s}".format(
                                      beam,
                                      "_".join(
                                          p for w, p in zip(weights, PARAMS[mode]) if w != 0),
                                  ),
                                  "current_{:d}".format(0))

    suffix = "" if mode == "normal" else "_couple"
    _copy_corrections(DATA_DIR[beam][mode], correction_dir, suffix)


def plot_corrections(beam):
    """ Plots all corrections from outputdir """
    for mode in ["normal", "coupling"]:
        corrections_dir = os.path.join(DATA_DIR[beam][mode], CORRECTIONS_SUBDIR)
        for subdir in os.listdir(corrections_dir):
            if not os.path.isfile(subdir):
                LOG.info("\n\n\n")
                LOG.info("Checking Corrections for {:s}".format(subdir))
                check_calculated_corrections.main(
                    accel=ACCEL,
                    lhc_mode=ACCELMODE,
                    beam=beam,
                    corrections_dir=os.path.join(corrections_dir, subdir),
                    model_dir=MODEL_DIR[beam],
                    meas_dir=DATA_DIR[beam][mode],
                    auto_scale=98.,
                    params=PARAMS[mode],
                    error_cut=ERROR_CUTS[beam][mode],
                    model_cut=MODEL_CUTS[beam][mode],
                    beta_file_name=BETA_FILE,
                    change_marker=True,
                )

# Helper #####################################################################


def _copy_corrections(src, dst, suffix):
    iotools.create_dirs(dst)
    filename = "changeparameters{:s}.madx".format(suffix)
    shutil.copy(os.path.join(src, filename),
                os.path.join(dst, filename))


# wrapper ####################################################################

def do_beam(beam):
    """ Wrapper for all functionality (per beam) """
    # prepare_model(beam)
    # create_responses(beam)
    # create_old_responses(beam)
    # correct_old_sum_diff_coupling(beam)
    # correct_old_sum_coupling(beam)
    # correct_old_all_normal(beam)
    # correct_old_NDX(beam)
    # correct_old_BBX_BBY_MUX_MUY_Q(beam)
    # correct_old_BB_NDX(beam)
    # for method in ["twiss", "madx"]:
    #     for iter in [0, 3]:
    #         correct_iter_all_normal(beam, method, iter)
    #         correct_iter_NDX(beam, method, iter)
    #         correct_iter_BBX_BBY_MUX_MUY_Q(beam, method, iter)
    #         correct_iter_BB_NDX(beam, method, iter)
    #         correct_iter_sum_diff_coupling(beam, method, iter)
    #         correct_iter_sum_coupling(beam, method, iter)
    plot_corrections(beam)


if __name__ == '__main__':
    do_beam(1)
    # do_beam(2)



