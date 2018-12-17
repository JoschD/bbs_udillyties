import os
import sys

# Beta-Beat Repo imports
beta_beta_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.append(beta_beta_path)

import madx_wrapper as madx
from utils import iotools
from utils.entrypoint import entrypoint, EntryPointParameters
from utils.entry_datatypes import BoolOrString
from utils import htcondor_wrapper as htc
from utils import logging_tools

from udillyties.madx_runners import irnl18_triplet_correction_template_control as tripcor_tmplt

# LOG = logging_tools.get_logger(__name__,
#                                level_console=logging_tools.DEBUG,
#                                fmt="%(asctime)s | %(levelname)7s | %(message)s | %(name)s"
#                                )
LOG = logging_tools.get_logger(__name__)

ERRORDEF_FILENAME = "WISE.errordef.{:04d}{:s}.tfs"


# main loop ####################################################################


def get_params():
    params = EntryPointParameters()
    params.add_parameter(
        flags="--beams",
        name="beams",
        type=int,
        nargs="*",
        choices=[1, 2],
        required=True,
        help="List of Beams to use",
    )
    params.add_parameter(
        flags="--xing",
        name="xing",
        nargs="+",
        type=BoolOrString,
        choices=[True, False, "IP1", "IP5"],
        required=True,
        help="List of crossing angles to apply. (True=all, False=none)",
    )
    params.add_parameter(
        flags="--otypes",
        name="optic_types",
        type=str,
        nargs="+",
        choices=["3030", "1515", "6015"],
        required=True,
        help="Optic types to use, e.g. '3030' for 30/30 betastar round optics.",
    )
    params.add_parameter(
        flags="--etypes",
        name="error_types",
        type=list,
        nargs="+",
        required=True,
        help="List of list-of-strings. Defines the errors to activate, e.g. 'A4'.",
    )
    params.add_parameter(
        flags="--elocs",
        name="error_locations",
        type=str,
        nargs="+",
        choices=["ALL", "IP1", "IP5"],
        required=True,
        help=("Defines the error location. "
              "Use 'ALL' for everywhere, 'IP#' for specific IP. "
              "Needs the wise-files to be available for these shananigans."),
    )
    params.add_parameter(
        flags="--seeds",
        name="seeds",
        type=int,
        nargs="+",
        required=True,
        help="List of seeds to use.",
    )
    params.add_parameter(
        flags="--cwd",
        name="cwd",
        type=str,
        required=True,
        help="Path to the current working directory.",
    )
    params.add_parameter(
        flags="--madxout",
        name="madx_out",
        type=str,
        help="Path to the root directory for madx-output.",
    )
    params.add_parameter(
        flags="--edef",
        name="errordef_dir",
        type=str,
        required=True,
        help="Path to the error-definition (WISE) files.",
    )
    params.add_parameter(
        flags="--moi",
        name="measure_of_interest",
        type=str,
        required=True,
        choices=["ptcrdt", "ptcampdet"],
        help="The measure to investigate. See choices.",
    )
    params.add_parameter(
        flags="--local",
        name="run_local",
        action="store_true",
        help="Flag to run the jobs on the local machine. Not suggested.",
    )
    params.add_parameter(
        flags="--duration",
        name="max_duration",
        help="Maximum duration to allow for htcondor jobs (ignored if run local).",
        default="workday",
    )
    return params


@entrypoint(get_params(), strict=True)
def main(opt):
    """ Main loop over all input variables """
    n_subs, n_jobs = get_number_of_jobs(opt)
    LOG.info("Creating {:d} submissions for {:d} madx-jobs.".format(n_subs, n_jobs))
    LOG.info("Starting main loop.")
    opt.madx_out = opt.madx_out if opt.madx_out is not None else opt.cwd
    madx_jobs = {}
    job_idx = 0
    for beam in opt.beams:
        for xing in opt.xing:
            for error_types in opt.error_types:
                for error_loc in opt.error_locations:
                    for seed in opt.seeds:
                        # define seed folder and error definition paths
                        seed_dir = get_seed_dir(opt.madx_out, seed)
                        errordef_path = get_errordef_path(opt.errordef_dir, seed, error_loc)

                        # assuming that we want 30/30 correction applied to the other optics
                        # we need to run the jobs in specific order
                        sequential_jobs = []
                        for optic_type in opt.optic_types:
                            job_idx += 1
                            LOG.info(
                                "Job No: {}/{}, ".format(job_idx, n_jobs) +
                                "Beam: {}, ".format(beam) +
                                "Xing: {}, ".format(xing) +
                                "eTypes: {}, ".format(",".join(error_types)) +
                                "eLoc: {}, ".format(error_loc) +
                                "Seed: {}, ".format(seed) +
                                "oType: {}, ".format(optic_type)
                            )
                            new_jobs = create_madx_jobs(
                                seed_dir, errordef_path,
                                beam, xing, error_types, error_loc, optic_type,
                                opt.measure_of_interest,
                            )
                            for njob in new_jobs:
                                sequential_jobs.append(njob)

                        madx_jobs[get_job_name(
                            beam, xing, error_types, error_loc, seed
                        )] = sequential_jobs

    run_madx_jobs(madx_jobs, opt.run_local, opt.cwd, opt.max_duration)


# Main Subfunctions ############################################################


def create_madx_jobs(seed_dir, errordef_path,
                     beam, xing, error_types, error_loc, optic_type,
                     measure_of_interest):
    """ Create madx jobs for:
        - the full current setup (given by the loop parameter)
        - the correction of the other beam by means of the former results
        - the correction by 30/30 optics results, if current optics are not 30/30

        These three jobs need therefore run in that order AND after 30/30 optics has been run.
        The first job exports results at the intermediate stages, whereas the latter two
        jobs only export the corrected results (and should hence run faster than the first job)
    """
    jobs = []

    # create output dir
    path = get_output_dir(seed_dir, xing, error_types, error_loc, optic_type)

    # write madx-jobfiles
    # normal job
    jobs.append(tripcor_tmplt.write_madx_job(
        path, errordef_path,
        beam, xing, error_types, optic_type,
        None, measure_of_interest)
    )

    # corrected by the corrections of the other beam
    correct_other_beam = tripcor_tmplt.get_correction_file(path, beam, optic_type)
    jobs.append(tripcor_tmplt.write_madx_job(
        path, errordef_path,
        get_other_beam(beam), xing, error_types, optic_type,
        correct_other_beam, measure_of_interest)
    )

    # corrected by the corrections of 30/30 round optics
    if "3030" != optic_type:
        path_3030 = get_output_dir(seed_dir, xing, error_types, error_loc, "3030")
        correct_3030 = tripcor_tmplt.get_correction_file(path_3030, beam, "3030")

        jobs.append(tripcor_tmplt.write_madx_job(
            path, errordef_path,
            beam, xing, error_types, optic_type,
            correct_3030, measure_of_interest)
        )
    return jobs


def run_madx_jobs(jobs, local, cwd, max_duration):
    """ Wrapper to run or submit the madx-jobs. """
    if local:
        for seq_jobs in jobs.values():
            for job in seq_jobs:
                madx.resolve_and_run_file(job, log_file="{}.log".format(job), cwd=cwd)

    else:
        for key in jobs:
            # create one folder per job to not get conflicts with the temp-subfolder
            job_dir = get_job_dir(cwd, key)
            bash = htc.write_madx_bash(job_dir, "", jobs[key])
            condor_job = htc.create_job_for_bashfile(bash, duration=max_duration)
            condor_sub = htc.create_subfile_from_job(job_dir, condor_job)
            htc.submit_jobfile(condor_sub)


# File Management ##############################################################


def get_nameparts_from_parameters(beam=None, xing=None, error_types=None, error_loc=None,
                                  seed=None, optic_type=None):
    """ Creates strings from the parameters to be used in names """
    parts = []

    if seed:
        parts.append("seed_{:04d}".format(seed))

    if beam:
        parts.append("b{:d}".format(beam))

    if optic_type:
        parts.append(optic_type)

    if error_types:
        parts.append("errors_{:s}".format("_".join(error_types)))

    if error_loc:
        parts.append("in_all_IPs" if "ALL" == error_loc else "in_{:s}".format(error_loc))

    if xing:
        xing_map = {
            True: "wXing",
            False: "noXing",
            "else": "{:s}Xing",
        }
        try:
            parts.append(xing_map[xing])
        except KeyError:
            parts.append(xing_map["else"].format(xing))

    return parts


def get_output_dir(seed_dir, xing, error_types, error_loc, optic_type):
    """ Return the output dir based on the input parameters """
    output_dir = os.path.join(
        seed_dir,
        "output_{:s}".format(".".join(get_nameparts_from_parameters(
            xing=xing, error_types=error_types, error_loc=error_loc, optic_type=optic_type
        )))
    )
    iotools.create_dirs(output_dir)
    return output_dir


def get_seed_dir(cwd, seed):
    """ Build the seed-dir-name and create it. """
    seed_dir = os.path.join(cwd, get_nameparts_from_parameters(seed=seed)[0])
    iotools.create_dirs(seed_dir)
    return seed_dir


def get_job_dir(cwd, id):
    """ Build the job-dir-name and create it. """
    job_dir = os.path.join(cwd, id)
    iotools.create_dirs(job_dir)
    return job_dir


def get_job_name(beam, xing, error_types, error_loc, seed):
    """ Return the name for the job """
    return ".".join(["job"] + get_nameparts_from_parameters(
        beam=beam, xing=xing, error_types=error_types, error_loc=error_loc, seed=seed
    ))


def get_errordef_path(path, seed, error_loc):
    """ Return the fullpath to the error definition file """
    error_loc = "" if "ALL" == error_loc else ".{:s}".format(error_loc)
    return os.path.join(path, ERRORDEF_FILENAME.format(seed, error_loc))


# Helper #######################################################################


def get_other_beam(beam):
    """ Returns the beam, that is not the current one. """
    return beam % 2 + 1


def get_number_of_jobs(opt):
    """ Short info about the "number" of jobs to be created
    (i.e. the number of calls to `create_madx_jobs()`, omitting the actual amount of jobs therein).
    """
    n_subs = (len(opt.beams) * len(opt.xing) * len(opt.error_types) *
              len(opt.error_locations) * len(opt.seeds))
    n_jobs = n_subs * len(opt.optic_types)

    return n_subs, n_jobs


# Script Mode ##################################################################


if __name__ == '__main__':
    main()
    # main(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingOnOff")
    # main(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingIP1")
    # main(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingIP5")
    # main(entry_cfg="./irnl18_triplet_correction_configs/rdt_study.ini", section="B1XingOnOff")
