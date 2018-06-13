import os

from generate_fullresponse_pandas import create_response
from global_correct_iterative import global_correction
from model.creator import create_instance_and_model
from utils import iotools
from utils import logging_tools

LOG = logging_tools.get_logger(__name__, level_console=logging_tools.DEBUG)

test_folder = os.path.abspath(os.path.join("tmp_model", "neu_model"))
data_folder = os.path.abspath(os.path.join("tmp_model", "correction_test_data"))

optics_param_arg = [
    "--optics_params",
    "MUX", "MUY", "Q", "DX", "DY", "BBX", "BBY", "BETX", "BETY",
    "F1001I", "F1001R", "F1010R", "F1010I"
]

variable_cat_args = [
    "--variables", "Q", "Qs"
]

accel_args = [
    "--accel", "lhc",
    "--lhcmode", "lhc_runII_2017",
    "--beam", "1",
]

creator_args = [
    "--type", "nominal",
    "--fullresponse",
    "--acd",
    "--nattunex", "0.3103",
    "--nattuney", "0.3199",
    "--drvtunex", "0.2983",
    "--drvtuney", "0.3349",
    "--optics", os.path.join(test_folder, "modifiers.madx"),
    '--output', test_folder,
    "--writeto", os.path.join(test_folder, "job.twiss.madx"),
    "--logfile", os.path.join(test_folder, "job.twiss.madx.log")
] + accel_args

create_madx_resp_args = [
    "--model_dir", test_folder,
    "--creator", "madx",
    "--outfile", os.path.join(test_folder, "fullresponse_madx"),
    "--tempdir", os.path.join(test_folder, "temp_folder")
] + accel_args

create_twiss_resp_args = [
    "--model_dir", test_folder,
    "--creator", "twiss",
    "--outfile", os.path.join(test_folder, "fullresponse_twiss")
] + accel_args


correct_args = [
    "--meas_dir", os.path.join(data_folder, "Beam1@Turn@2017_05_25@19_07_04_535/getLLM_output"),
    "--model_dir", test_folder,
    "--max_iter", "3",
    "--debug",
] + accel_args + optics_param_arg


def model_creation():
    iotools.create_dirs(test_folder)
    iotools.copy_item(os.path.join(data_folder, "modifiers.madx"),
                      os.path.join(test_folder, "modifiers.madx"))

    LOG.info("Creating Model")
    create_instance_and_model(creator_args)


def madx_correction_test():
    LOG.info("Creating MADX response")
    create_response(create_madx_resp_args + variable_cat_args + optics_param_arg)

    LOG.info("Correcting Iteratively MADX-Response")
    global_correction(correct_args +
                      ["--fullresponse", os.path.join(test_folder, "fullresponse_madx"),
                       "--output_dir", os.path.join(test_folder, "corrected_madx")])


def twiss_correction_test():
    LOG.info("Creating Twiss response")
    create_response(create_twiss_resp_args + variable_cat_args + optics_param_arg)

    LOG.info("Correcting Iteratively twiss_Response")
    global_correction(correct_args +
                      ["--fullresponse", os.path.join(test_folder, "fullresponse_twiss"),
                       "--output_dir", os.path.join(test_folder, "corrected_twiss")])


def twiss_response_creation_test():
    with logging_tools.DebugMode():
        create_response(create_twiss_resp_args + variable_cat_args + optics_param_arg)
    LOG.info("\n\n\n")
    LOG.info("Creating Twiss response.")
    with logging_tools.DebugMode():
        create_response(create_twiss_resp_args + variable_cat_args)


def correction_debugging_test():
    LOG.info("Running debugging test.")
    args = ['--accel', 'lhc', '--lhcmode', 'lhc_runII_2017', '--beam', '1',
            '--meas_dir', '/home/jdilly/link_gui_out/2018-03-23/LHCB1/Results/18-06-59_NORMALANALYSIS_SUSSIX_1',
            '--model_dir', '/home/jdilly/link_gui_out/2018-03-23/models/LHCB1/multiturn_highbeta_colltunes',
            # '--fullresponse', '/media/jdilly/Storage/Repositories/Gui_Output/2018-03-23/models/LHCB1/multiturn_highbeta_colltunes/Fullresponse_pandas',
            '--variables', 'coupling_knobs',
            '--optics_params', 'F1001R', 'F1001I', 'F1010R', 'F1010I', 'DY',
            '--weights', '1', '1', '0', '0', '0',
            '--error_cut', '0.02', '0.02', '0.02', '0.02', '0.02',
            '--model_cut', '0.0', '0.0', '0.0', '0.0', '0.01',
            '--output_dir', '/home/jdilly/link_gui_out/2018-03-22/LHCB1/Results/18-06-59_NORMALANALYSIS_SUSSIX_1',
            '--svd_cut', '0.01',
            '--beta_file_name', 'getbeta',
            '--max_iter', '3',
            # "--update_response",
            # '--debug'
            ]
    global_correction(args)


def response_debugging_test():
    args = [ '--accel', 'lhc', '--lhcmode', 'lhc_runII_2017', '--beam', '1',
             '--creator', 'madx',
             '--deltak', '0.00002',
             '--variables', 'coupling_knobs',
             '--outfile', '/home/jdilly/link_gui_out/2018-03-22/models/LHCB1/multiturn_highbeta_colltunes/Fullresponse_pandas',
             '--model_dir', '/home/jdilly/link_gui_out/2018-03-22/models/LHCB1/multiturn_highbeta_colltunes',
             '--debug']
    create_response(args)


if __name__ == "__main__":
    # response_debugging_test()
    # correction_debugging_test()
    model_creation()
    # twiss_response_creation_test()
    # madx_correction_test()
    # twiss_correction_test()
