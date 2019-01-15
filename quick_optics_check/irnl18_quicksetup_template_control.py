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
    "NOMINALMACHINE", "ALLAPPLIED"
]

# IDs for output files/stages
IDS = {
    "NOMINALMACHINE": "nominal",
    "ALLAPPLIED": "all_errors",
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


def _get_output_snippet(path, beam, snippet_name):
    """ Return the output-creating snippets to be placed into the madx file """
    snippet = getattr(madx_snippets, snippet_name)
    ids = IDS.copy()

    return {out: snippet(path, "b{:d}.{:s}".format(beam, ids[out]))
            for out in ids.keys()}


def _get_job_name(path, beam):
    """ Get the name of the job file """
    file_parts = os.path.splitext(os.path.basename(MADX_TEMPLATE))
    out_parts = [file_parts[0].replace("template", "job"),
                 "b{:d}".format(beam),
                 file_parts[1].strip(".")]
    return os.path.join(path, ".".join(out_parts))


# Public Functions ################################################################


def fill_madx_template(params):
    """ Manual way to get the template content

        Params is filled with default values. See _get_default_parameters() for details.
    """
    params = _get_default_parameters(params)
    with open(MADX_TEMPLATE, "r") as f:
        template = f.read()
    return template % params


def write_madx_job(output_path, errordef_path,
                   beam, xing, error_types, optic_type,
                   madx_out_snippet):
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
        madx_out_snippet: see shortforms in madx/madx_snippets

    """
    params = {
        "BEAM": str(beam),
        "TYPE": optic_type,
        "ERRORDEF": errordef_path
    }

    params.update(_get_crossing_params_for_optics(optic_type, xing))
    params.update(_get_errortypes_params(error_types))
    params.update(_get_output_snippet(output_path, beam, madx_out_snippet))

    job_path = _get_job_name(output_path, beam)
    with open(job_path, "w") as f:
        f.write(fill_madx_template(params))
    return job_path


# Script Mode ##################################################################


if __name__ == '__main__':
    raise EnvironmentError("{:s} is not supposed to run as main.".format(__file__))
