import os
import sys

# Beta-Beat Repo imports
beta_beta_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.append(beta_beta_path)

from madx import code_snippets
from utils import logging_tools

LOG = logging_tools.get_logger(__name__)

TEMPLATEDIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATEMAP = {
    "LHC": "template.2018.LHC.IRNL.squeezed.triplet_correction.madx",
    # "LHC": "template.2018.LHC.IRNL.squeezed.manual_feeddown.madx",  # MANUAL FEEDDOWN
    "HLLHC": "template.2018.HLLHC.IRNL.squeezed.triplet_correction.madx",
}

CORRECTIONS_FILENAME = "MCX.setting.{:s}.{:s}.mad"

STAGE_ORDER = {
    "LHC": ["NOMINALMACHINE", "ARCAPPLIED", "MQXAPPLIED",  "MBIPAPPLIED",
             "ALLAPPLIED", "CORRECTED"],
    "HLLHC": ["NOMINALMACHINE", "ARCAPPLIED", "IPAPPLIED",  "CORRECTED"],
}


# IDs for output files/stages
IDS = {
    "NOMINALMACHINE": "nominal",
    "ARCAPPLIED": "errors_arc",
    "MQXAPPLIED": "errors_mqx",
    "MBIPAPPLIED": "errors_mb_ip",
    "ALLAPPLIED": "errors_all",
    "IPAPPLIED": "errors_ip",
    "CORRECTED": "corrected"
}

SUPPORTED_MACHINES = ["LHC", "HLLHC"]
CTA_IDS = ["before_cta", "after_cta"]


class TemplateControl:

    def __init__(self, machine):
        if machine not in SUPPORTED_MACHINES:
            raise NotImplementedError("Machine '{:s}' not implemented.".format(machine))
        self.machine = machine
        self.template = self._get_template_for_machine(machine)

    # Params #######################################################################
    def _get_default_parameters(self, new_values):
        """ Parameters to be filled in MADX-Script """

        if self.machine == "LHC":
            no_default = ["BEAM", "TYPE", "ERRORDEF", "CORRECTIONS"]
            default = {
                # Beam Parameters
                "QX": "62.31",
                "QY": "60.32",
                "CHROMX": "3",
                "CHROMY": "3",
                # Settings
                "USETHIN": "1",
                "ARCERRORS": "1",
                "CALCCORRECTTRIP": "1",
                # Outputs
                "NOMINALMACHINE": "",
                "ARCAPPLIED": "",
                "MQXAPPLIED": "",
                "MBIPAPPLIED": "",
                "ALLAPPLIED": "",
                "CORRECTED": "",
                #other
                "OFF5V": "0",
            }
        elif self.machine == "HLLHC":
            no_default = ["BEAM", "TYPE", "ERRORDEF", "CORRECTIONS"]
            default = {
                # Beam Parameters
                "QX": "62.31",
                "QY": "60.32",
                "CHROM": "3",
                "NRJ": "7000.0",
                # Settings
                "ONDISP": "1",
                "CALCCORRECTTRIP": "1",
                "ARCERRORS": "1",
                "CORRECTD2": "0",
                "CORRECTMCBX": "0",
                "LSF": "0",
                "MOPOWER": "0",
                "ONALICE": "0",
                "ONLHCB": "0",
                # Outputs
                "NOMINALMACHINE": "",
                "ARCAPPLIED": "",
                "IPAPPLIED": "",
                "CORRECTED": "",
            }

        not_found = [nf for nf in no_default if nf not in new_values]
        if any(not_found):
            raise ValueError("Required parameters '{}' not found.".format(not_found))

        # crossing angles and separation bumps
        for idx in [1, 2, 5, 8]:
            for prefix in ["XING", "SEP", "PHI"]:
                default["{:s}{:d}".format(prefix, idx)] = "0"

        # applied errors
        for idx in range(1, 12):
            for orientation in ["A", "B"]:
                default["{:s}{:d}".format(orientation, idx)] = "0"

        # return dictionary filled with defaults and new values
        default.update(new_values)
        return default

    def _get_crossing_params_for_optics(self, optic_type, xing):
        """ Return the crossing parameters for optics type and crossing scheme """
        if optic_type[0:2] == optic_type[2:4]:
            otype = "round"
        else:
            otype = "flat"

        if self.machine == "LHC":
            if optic_type == "flat":
                raise NotImplementedError("CHECK SEPARATION SIGNS FOR FLAT ORBIT!!")
            mapping = {
                "round": {
                    "IP1": {"XING1": "160", "PHI1": "90", "SEP1": "-0.55"},
                    "IP5": {"XING5": "160", "PHI5": "0",  "SEP5": "0.55"},
                },
                "flat": {
                    "IP1": {"XING1": "160", "PHI1": "0",  "SEP1": "-0.55"},
                    "IP5": {"XING5": "160", "PHI5": "90", "SEP5": "0.55"},
                },
            }
        elif self.machine == "HLLHC":
            mapping = {
                "round": {
                    "IP1": {"XING1": "295",  "PHI1": "90", "SEP1": "-0.75"},
                    "IP5": {"XING5": "295",  "PHI5": "0",  "SEP5": "0.75"},
                    "IP2": {"XING2": "170",  "PHI2": "90", "SEP2": "2",  "ONALICE": "1"},
                    "IP8": {"XING8": "-250", "PHI8": "0",  "SEP8": "-2", "ONLHCB":  "1"},
                },
            }
            if otype == "flat":
                raise NotImplementedError("Flat optics not implemented for HLLHC yet.")

        result = {}
        if xing:
            # return appropriate settings (differing from defaults, which is no crossing)
            if not isinstance(xing, list):  # use all
                xing = mapping[otype].keys()
            [result.update(mapping[otype][sub]) for sub in xing]
        return result

    def _get_seedran(self, seed):
        if self.machine == "LHC":
            return {}  # not needed in LHC
        elif self.machine == "HLLHC":
            return {"SEEDRAN": str(seed)}

    @staticmethod
    def _get_errortypes_params(error_types):
        """ Return a dictionary with activated errors of present kinds (e.g. A4, B3) """
        return {et: "1" for et in error_types}

    def _get_output_snippets(self, path, beam, correct_by, measure_of_interest):
        """ Return the output-creating snippets to be placed into the madx file """
        snippet = {
            "ptcrdt": code_snippets.get_ptc_twiss_rdt,
            "ptcampdet": code_snippets.get_ptc_amplitude_detuning,
        }

        ids = IDS
        stage_order = STAGE_ORDER[self.machine]
        if correct_by is not None:
            ids = {"CORRECTED": "{:s}_{:s}".format(
                ids["CORRECTED"], self._get_correct_by_base(correct_by))
            }
            stage_order = ["CORRECTED"]

        return {out: snippet[measure_of_interest](path, "b{:d}.{:s}".format(beam, ids[out]))
                for out in stage_order}

    def _get_corrections_params(self, path, beam, optic_type, correct_by):
        """ Return the parameters for the triplet correction """
        if correct_by is not None:
            calc = "0"
            correct = correct_by
        else:
            calc = "1"
            correct = self.get_correction_file(path, beam, optic_type)

        return {
            "CALCCORRECTTRIP": calc,
            "CORRECTIONS": correct,
        }

    @staticmethod
    def _get_correction_file(path, beam, optic_type):
        """ Get the filename for the triplet-corrections file. """
        return os.path.join(path, CORRECTIONS_FILENAME.format("b{:d}".format(beam), optic_type))

    @staticmethod
    def _get_correct_by_base(correct_by):
        """ Return a short filename for the corrections settings file """
        idcs = [i for i, s in enumerate(CORRECTIONS_FILENAME.split(".")) if s.startswith("{")]
        parts = os.path.basename(correct_by).split(".")
        return "by_{:s}".format("_".join([parts[idx] for idx in idcs]))

    def _get_job_name(self, path, beam, corrected_by):
        """ Get the name of the job file """
        file_parts = os.path.splitext(os.path.basename(self.template))
        out_parts = [
            file_parts[0].replace("template", "job"),
            "b{:d}".format(beam),
        ]
        if corrected_by is not None:
            out_parts.append(self._get_correct_by_base(corrected_by))
        out_parts.append(file_parts[1].strip("."))
        return os.path.join(path, ".".join(out_parts))

    @staticmethod
    def _get_template_for_machine(machine):
        return os.path.join(TEMPLATEDIR, TEMPLATEMAP[machine])

    # Public Functions ################################################################

    def get_correction_file(self, path, beam, optic_type):
        """ Return the path of the correction file with the naming convention. """
        return self._get_correction_file(path, beam, optic_type)

    def fill_madx_template(self, params):
        """ Manual way to get the template contend

            Params is filled with default values. See _get_default_parameters() for details.
        """
        params = self._get_default_parameters(params)
        with open(self.template, "r") as f:
            template = f.read()
        return template % params

    @staticmethod
    def get_cta_names(beam):
        return ["twiss.b{:d}.{}.tfs".format(beam, id) for id in CTA_IDS]

    def write_madx_job(self, output_path, errordef_path, seed,
                       beam, xing, error_types, optic_type,
                       correct_by, measure_of_interest, manual={}):
        """ Prepare the template content and write it into a job

        Args:
            output_path: path to the output directory
            errordef_path: path to the wise-errordefinition file to use
            beam: [12]
            xing: False, True or list of IPs
            error_types: "[AB][1-11]"
            optic_type: "3030, "1515" or "6015"
            correct_by: path to magnet settings file
                        (naming conventions need to apply, see get_correction_file())
            measure_of_interest: either 'ptcrdt' or 'ptcampdet'

        """
        params = {
            "BEAM": str(beam),
            "TYPE": optic_type,
            "ERRORDEF": errordef_path,
        }

        params.update(self._get_seedran(seed))
        params.update(self._get_crossing_params_for_optics(optic_type, xing))
        params.update(self._get_errortypes_params(error_types))
        params.update(self._get_output_snippets(output_path, beam, correct_by, measure_of_interest))
        params.update(self._get_corrections_params(output_path, beam, optic_type, correct_by))
        params.update({"OUTPATH": output_path})
        params.update(manual)

        job_path = self._get_job_name(output_path, beam, correct_by)
        with open(job_path, "w") as f:
            f.write(self.fill_madx_template(params))
        return job_path


# Script Mode ##################################################################


if __name__ == '__main__':
    raise EnvironmentError("{:s} is not supposed to run as main.".format(__file__))
