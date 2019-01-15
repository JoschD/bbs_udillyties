""" Calculated Beta Star via Polyfit from a model, that does not contain values at the IPs.
 Not thoroughly tested.
 """
import os

import madx_wrapper
from utils.dict_tools import ArgumentError

from utils.entrypoint import EntryPointParameters, entrypoint
from utils import logging_tools
from model import manager
import numpy as np
from tfs_files import tfs_pandas
from model.accelerators.accelerator import AcceleratorDefinitionError

LOG = logging_tools.get_logger(__name__)

TWISS_CORRECT = "twiss_corrected"

# This is why this function is LHC specific.
# Generalize IPs and Names for all accels:
IPS = [1,2,5,8]
QUADS = r"^MQXA\.1[LR]{ip:d}$"
BPMS = r"^BPMSW\.1[LR]{ip:d}\.B[12]$"
IP = "IP{ip:d}"

LOCATION_COLUMN = "S"
BETA_COLUMN = "BET{plane:s}"
PLANES = "XY"
RES_COLUMNS = ["LABEL", "BETASTAR", "WAIST", "BETAWAIST"]
RESULTS_PREFIX = "betaip_"
RESULTS_SUFFIX = ".tfs"

def get_params():
    params = EntryPointParameters()
    params.add_parameter(
        flags="--corrections",
        help="Path to the directory containing the measurement files.",
        name="corrections",
        nargs="+",
        default=[],
        type=str,
    )
    params.add_parameter(
        flags="--labels",
        help="Path to the directory containing the measurement files.",
        name="labels",
        nargs="+",
        default=[],
        type=str,
    )
    params.add_parameter(
        flags="--model_dir",
        help="Path to the model to use.",
        name="model_dir",
        required=True,
        type=str,
    )
    params.add_parameter(
        flags="--output_dir",
        help="Path to the model to use.",
        name="output_dir",
        required=True,
        type=str,
    )
    params.add_parameter(
        flags="--optics_file",
        help=("Path to the optics file to use. If not present will default to "
              "model_path/modifiers.madx, if such a file exists."),
        name="optics_file",
        type=str,
    )

    return params

@entrypoint(get_params())
def main(opt, accel_opt):
    if len(opt.corrections) or len(opt.labels):
        if len(opt.corrections) != len(opt.labels):
            raise ArgumentError("Length of labels and corrections need to be equal.")

    accel_cls = manager.get_accel_class(accel_opt)
    if "lhc" not in accel_cls.NAME:
        raise AcceleratorDefinitionError("Only implemented for LHC")

    accel_inst = accel_cls(model_dir=opt.model_dir)
    if opt.optics_file is not None:
        accel_inst.optics_file = opt.optics_file

    locations = _get_locations_of_interest(accel_inst)

    results = {}
    results["main"] = _get_result(accel_inst, locations)
    for correction, label in zip(opt.corrections, opt.labels):
        results[label] = _get_result(accel_inst, locations, correction)

    _write_results(opt.output_dir, results)


# Get Data #####################################################################


def _get_locations_of_interest(accel_inst):
    """ Return the locations sorted by IP"""
    locations = {}
    for ip in IPS:
        locations[ip] = _get_kmod_elements(accel_inst, ip)
    return locations


def _get_kmod_elements(accel_inst, ip):
    """ Return the elements used for fit in perfect order"""
    elements = accel_inst.get_elements_tfs().index
    bpm_mask = elements.str.match(BPMS.format(ip=ip))
    quad_mask = elements.str.match(QUADS.format(ip=ip))

    bpm_names = elements[bpm_mask].sort_values()  # L < R
    quad_names = elements[quad_mask].sort_values()
    ip_name = IP.format(ip=ip)

    # take the drift before the right MQXA to get beta at the magnets end
    quad_names[1] = elements[elements.get_loc(quad_names[1])-1]
    return [ip_name, quad_names[0], bpm_names[0], bpm_names[1], quad_names[1]]


# Calculate Result #############################################################


def _get_result(accel_inst, output_dir, locations, correction=None):
    """ Main function to gather the results for one tfs file """
    elements = _get_elements_by_ip(accel_inst, output_dir, locations, correction)

    res = tfs_pandas.TfsDataFrame(
        index=[l[0] for l in locations.values()],
        columns=RES_COLUMNS,
    )
    for ip in elements.keys():
        res.append(_calc_result(elements[ip]))
    return res


def _get_elements_by_ip(accel_inst, output_dir, locations, correction):
    """ Get Elements in corret order """
    if correction:
        elements = _get_elements_from_madx(accel_inst, output_dir, locations, correction)
    else:
        elements = accel_inst.get_elements_tfs()

    elements_by_ip = {}
    for ip in elements.keys():
        elements_by_ip[ip] = elements[locations[ip]]

    return elements_by_ip


def _get_elements_from_madx(accel_inst, output_dir, locations, correction):
    """ Create and call the madx jobs to apply the corrections """
    corr_name = os.path.splitext(os.path.basename(correction))[0]
    twiss_path = os.path.join(output_dir, "{:s}_{:s}.dat".format(TWISS_CORRECT, corr_name))

    job_content = _get_madx_job(accel_inst, twiss_path, locations, correction)
    madx_wrapper.resolve_and_run_string(
        job_content,
        output_file=os.path.join(output_dir, "job.corrections.madx"),
        log_file=os.path.join(output_dir, "job.corrections.log"),
    )

    return tfs_pandas.read_tfs(twiss_path, index="NAME")


def _get_madx_job(accel_inst, output, locations, correction):
    """ Creates the basic job-string. """
    job_content = accel_inst.get_basic_seq_job()
    job_content += "select, flag=twiss, clear;\n"
    for loc in [l for ip in locations.keys() for l in locations[ip]]:
        job_content += "select, flag=twiss, pattern='{:s}$', ".format(loc)
    job_content += "column=NAME,S,BETX,BETY;\n\n"

    if correction:
        job_content += "call, file='{:s}';\n".format(correction)
    job_content += "twiss, file='{:s}';\n".format(output)
    return job_content


def _calc_result(elements_ip):
    """ Main Calcluation function to get the result data """
    ip_name = elements_ip.index[0]
    # ip_pos = elements_ip.at[ip_name, LOCATION_COLUMN]
    elements_fit = elements_ip.drop(ip_name, axis=0)
    res = tfs_pandas.TfsDataFrame(columns=RES_COLUMNS).set_index(RES_COLUMNS[0])
    for plane in PLANES:
        p, resids, rank, s, rcond = np.polyfit(
            x=elements_fit.loc[:, LOCATION_COLUMN],
            y=elements_fit.loc[:, BETA_COLUMN.format(plane)],
            deg=2,
            full=True,
        )
        # x^2 * p[0] + x * p[1] + p[2]
        res.loc["{:s}.{:s}".format(elements_ip.index[0], plane.upper())] = [  # label
            elements_ip.at[ip_name, BETA_COLUMN.format(plane)],       # betastar
            - p[1] / (2 * p[0]),                                      # waist
            - p[1]**2 / (4*p[0]) + p[2],                              # betawaist
        ]
    return res


# Write Results ################################################################


def _write_results(output_dir, results):
    for label in results.keys():
        file_path = os.path.join(output_dir, "{:s}{:s}{:s}".format(
            RESULTS_PREFIX, label, RESULTS_SUFFIX
        ))
        tfs_pandas.write_tfs(file_path, results[label])


