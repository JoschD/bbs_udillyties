import os
import sys

# Beta-Beat Repo imports
beta_beta_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.append(beta_beta_path)

from madx import madx_snippets
from utils import logging_tools

LOG = logging_tools.get_logger(__name__)

MADX_TEMPLATE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             "template.2018.IRNL.squeezed.triplet_correction.madx"))

CORRECTIONS_FILENAME = "MCX.setting.{:s}.{:s}.mad"

STAGE_ORDER = [
    "NOMINALMACHINE", "ARCAPPLIED", "MQXAPPLIED",  "MBIPAPPLIED", "ALLAPPLIED", "CORRECTED"
]

# IDs for output files/stages
IDS = {
    "NOMINALMACHINE": "nominal",
    "ARCAPPLIED": "arc",
    "MQXAPPLIED": "mqx",
    "MBIPAPPLIED": "mb_ip",
    "ALLAPPLIED": "all_errors",
    "CORRECTED": "corrected"
}


# Params #######################################################################


def _get_default_parameters(new_values):
    """ Parameters to be filled in MADX-Script """
    no_default = ["BEAM", "TYPE", "ERRORDEF", "CORRECTIONS"]

    not_found = [nf for nf in no_default if nf not in new_values]
    if any(not_found):
        raise ValueError("Required parameters '{}' not found.".format(not_found))

    # Some defaults
    default = {
        # Beam Parameters
        "QX": "62.31",
        "QY": "60.32",
        "CHROMX": "3",
        "CHROMY": "3",
        # Settings
        "USETHIN": "1",
        "ARCERRORS": "0",
        "CALCCORRECTIONS": "1",
        # Outputs
        "NOMINALMACHINE": "",
        "ARCAPPLIED": "",
        "MQXAPPLIED": "",
        "MBIPAPPLIED": "",
        "ALLAPPLIED": "",
        "CORRECTED": "",
    }

    # crossing angles and separation bumps
    for idx in [1,2,5,8]:
        for prefix in ["XING", "SEP", "PHI"]:
            default["{:s}{:d}".format(prefix, idx)] = "0"

    # applied errors
    for idx in range(1, 12):
        for orientation in ["A", "B"]:
            default["{:s}{:d}".format(orientation, idx)] = "0"

    # return dictionary filled with defaults and new values
    default.update(new_values)
    return default


def _get_crossing_params_for_optics(optic_type, xing):
    """ Return the crossing parameters for optics type and crossing scheme """
    mapping = {
        "round": {
            "IP1": {"XING1": "150", "PHI1": "90"},
            "IP5": {"XING5": "150", "PHI5": "0"},
        },
        "flat": {
            "IP1": {"XING1": "150", "PHI1": "0"},
            "IP5": {"XING5": "150", "PHI5": "90"},
        },
    }

    if xing:
        # get optics type first
        if optic_type[0:2] == optic_type[2:4]:
            otype = "round"
        else:
            otype = "flat"

        # return appropriate settings (differing from defaults, which is no crossing)
        try:
            return mapping[otype][xing]
        except KeyError:
            # xing enabled for all ips
            result = {}
            [result.update(mapping[otype][sub]) for sub in mapping[otype]]
            return result
    return {}  # will use all defaults


def _get_errortypes_params(error_types):
    """ Return a dictionary with activated errors of present kinds (e.g. A4, B3) """
    return {et: "1" for et in error_types}


def _get_output_snippets(path, beam, correct_by, measure_of_interest):
    """ Return the output-creating snippets to be placed into the madx file """
    snippet = {
        "ptcrdt": madx_snippets.get_ptc_twiss_rdt,
        "ptcampdet": madx_snippets.get_ptc_amplitude_detuning,
    }

    ids = IDS.copy()
    if correct_by is not None:
        ids = {"CORRECTED": "{:s}_{:s}".format(
            ids["CORRECTED"], _get_correct_by_base(correct_by))
        }

    return {out: snippet[measure_of_interest](path, "b{:d}.{:s}".format(beam, ids[out]))
            for out in ids.keys()}


def _get_corrections_params(path, beam, optic_type, correct_by):
    """ Return the parameters for the triplet correction """
    if correct_by is not None:
        calc = "0"
        correct = correct_by
    else:
        calc = "1"
        correct = get_correction_file(path, beam, optic_type)

    return {
        "CALCCORRECTIONS": calc,
        "CORRECTIONS": correct,
    }


def _get_correction_file(path, beam, optic_type):
    """ Get the filename for the triplet-corrections file. """
    return os.path.join(path, CORRECTIONS_FILENAME.format("b{:d}".format(beam), optic_type))


def _get_correct_by_base(correct_by):
    """ Return a short filename for the corrections settings file """
    idcs = [i for i,s in enumerate(CORRECTIONS_FILENAME.split(".")) if s.startswith("{")]
    parts = os.path.basename(correct_by).split(".")
    return "by_{:s}".format("_".join([parts[idx] for idx in idcs]))


def _get_job_name(path, beam, corrected_by):
    """ Get the name of the job file """
    file_parts = os.path.splitext(os.path.basename(MADX_TEMPLATE))
    out_parts = [
        file_parts[0].replace("template", "job"),
        "b{:d}".format(beam),
    ]
    if corrected_by is not None:
        out_parts.append(_get_correct_by_base(corrected_by))
    out_parts.append(file_parts[1].strip("."))
    return os.path.join(path, ".".join(out_parts))


# Public Functions ################################################################


def get_correction_file(path, beam, optic_type):
    """ Return the path of the correction file with the naming convention. """
    return _get_correction_file(path, beam, optic_type)


def fill_madx_template(params):
    """ Manual way to get the template contend

        Params is filled with default values. See _get_default_parameters() for details.
    """
    params = _get_default_parameters(params)
    with open(MADX_TEMPLATE, "r") as f:
        template = f.read()
    return template % params


def write_madx_job(output_path, errordef_path,
                   beam, xing, error_types, optic_type,
                   correct_by, measure_of_interest):
    """ Prepare the template content and write it into a job

    Args:
        output_path: path to the output directory
        errordef_path: path to the wise-errordefinition file to use
        beam: [12]
        xing: False, True or IP[15]
        error_types: "[AB][1-11]"
        optic_type: "3030, "1515" or "6015"
        correct_by: path to magnet settings file
                    (naming conventions need to apply, see get_correction_file())
        measure_of_interest: either 'ptcrdt' or 'ptcampdet'

    """
    params = {
        "BEAM": str(beam),
        "TYPE": optic_type,
        "ERRORDEF": errordef_path
    }

    params.update(_get_crossing_params_for_optics(optic_type, xing))
    params.update(_get_errortypes_params(error_types))
    params.update(_get_output_snippets(output_path, beam, correct_by, measure_of_interest))
    params.update(_get_corrections_params(output_path, beam, optic_type, correct_by))

    job_path = _get_job_name(output_path, beam, correct_by)
    with open(job_path, "w") as f:
        f.write(fill_madx_template(params))
    return job_path


# Script Mode ##################################################################


if __name__ == '__main__':
    raise EnvironmentError("{:s} is not supposed to run as main.".format(__file__))
