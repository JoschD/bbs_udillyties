import os
import sys

# Beta-Beat Repo imports
beta_beta_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.append(beta_beta_path)

import madx_wrapper as madx
from utils import iotools
from utils.entrypoint import entrypoint, EntryPointParameters
from utils.entry_datatypes import BoolOrList, DictAsString, BoolOrString
from utils import htcondor_wrapper as htc
from utils import logging_tools

from udillyties.madx_runners import irnl18_triplet_correction_template_control as tripcor_tmplt
from udillyties.helpers import find_file_by_pattern

# LOG = logging_tools.get_logger(__name__,
#                                level_console=logging_tools.DEBUG,
#                                fmt="%(asctime)s | %(levelname)7s | %(message)s | %(name)s"
#                                )
LOG = logging_tools.get_logger(__name__)


# main loop ####################################################################


def get_params():
    params = EntryPointParameters()
    params.add_parameter(
        flags="--machine",
        name="machine",
        type=str,
        choices=["LHC", "HLLHC"],
        default="LHC",
        help="Machine to use",
    )
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
        type=BoolOrList,
        required=True,
        help="List of crossing angles to apply. (True=all, False=none)",
    )
    params.add_parameter(
        flags="--otypes",
        name="optic_types",
        type=str,
        nargs="+",
        choices=["3030", "1515", "6015", "4040"],
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
        flags="--edefdir",
        name="errordef_dir",
        type=str,
        required=True,
        help="Path to the error-definition (WISE) files.",
    )
    params.add_parameter(
        flags="--edefmask",
        name="errordef_mask",
        type=str,
        required=True,
        help="Mask of the error-definition (WISE) files.",
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
        default="nextweek",
    )
    params.add_parameter(
        flags="--wother",
        name="with_other_corrections",
        help="do also the other corrections, i.e. from 3030 and other beam.",
        action="store_true",
    )
    params.add_parameter(
        flags="--unstage",
        name="unused_stages",
        type=str,
        nargs="+",
        default=[],
        help="List of unused stages.",
    )
    params.add_parameter(
        flags="--resume",
        name="resume_jobs",
        action="store_true",
        help="Only do jobs that did not work.",
    )
    params.add_parameter(
        flags="--manual",
        name="manual",
        help="Manual override of parameters.",
        type=DictAsString,
        default={},
    )
    return params


@entrypoint(get_params(), strict=True)
def main(opt):
    """ Main loop over all input variables """
    opt = check_opt(opt)
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

                        # assuming that we want 30/30 correction applied to the other optics
                        # we need to run the jobs in specific order
                        sequential_jobs = []
                        for optic_type in opt.optic_types:
                            if _job_needs_to_be_done(seed_dir, opt.machine, beam, xing,
                                                     error_types, error_loc, optic_type,
                                                     opt.resume_jobs):
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
                                    opt.machine,
                                    seed_dir, opt.errordef_dir, opt.errordef_mask,
                                    seed,
                                    beam, xing, error_types, error_loc, optic_type,
                                    opt.measure_of_interest,
                                    opt.with_other_corrections,
                                    opt.manual,
                                )
                                for njob in new_jobs:
                                    sequential_jobs.append(njob)

                        if len(sequential_jobs) > 0:
                            madx_jobs[get_job_name(
                                beam, xing, error_types, error_loc, seed
                            )] = sequential_jobs

    run_madx_jobs(madx_jobs, opt.run_local, opt.cwd, opt.max_duration)


# Main Subfunctions ############################################################


def _job_needs_to_be_done(seed_dir, machine, beam, xing, error_types, error_loc, optic_type,
                          resume_jobs):
    if not resume_jobs:
        return True

    path = get_output_dir(seed_dir, xing, error_types, error_loc, optic_type)
    corrections = tripcor_tmplt.CORRECTIONS_FILENAME.format("b{:d}".format(beam), optic_type)
    corrections = corrections.replace(".", r"\.")  # for regex
    last_stage = tripcor_tmplt.STAGE_ORDER[machine][-1]
    last_file_pattern = r"\." + "b{:d}".format(beam) + r"\." + tripcor_tmplt.IDS[last_stage] + r"\."

    if (not len(find_file_by_pattern(path, corrections)) or
            not len(find_file_by_pattern(path, last_file_pattern))):
        LOG.warn("Not all output files present for Beam {:d} in '{:s}'".format(beam, path))
        beam_files = find_file_by_pattern(path, r"\." + "b{:d}".format(beam) + r"\.")
        for bf in beam_files:
            LOG.warn("  Removing '{:s}'".format(bf))
            os.remove(bf)
        return True
    return False


def create_madx_jobs(machine, seed_dir, errordef_dir, errordef_mask, seed,
                     beam, xing, error_types, error_loc, optic_type,
                     measure_of_interest, do_other_corrections, manual):
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
    control_tmplt = tripcor_tmplt.TemplateControl(machine)
    errordef_path = get_errordef_path(errordef_dir, errordef_mask, seed, error_loc)

    # write madx-jobfiles
    # normal job
    jobs.append(control_tmplt.write_madx_job(
        path, errordef_path, seed,
        beam, xing, error_types, optic_type,
        None, measure_of_interest, manual)
    )

    if do_other_corrections:
        # corrected by the corrections of the other beam
        correct_other_beam = control_tmplt.get_correction_file(path, beam, optic_type)
        jobs.append(control_tmplt.write_madx_job(
            path, errordef_path, seed,
            get_other_beam(beam), xing, error_types, optic_type,
            correct_other_beam, measure_of_interest, manual)
        )

        # corrected by the corrections of 30/30 round optics
        if "3030" != optic_type:
            path_3030 = get_output_dir(seed_dir, xing, error_types, error_loc, "3030")
            correct_3030 = control_tmplt.get_correction_file(path_3030, beam, "3030")

            jobs.append(control_tmplt.write_madx_job(
                path, errordef_path, seed,
                beam, xing, error_types, optic_type,
                correct_3030, measure_of_interest, manual)
            )
    return jobs


def run_madx_jobs(jobs, local, cwd, max_duration):
    """ Wrapper to run or submit the madx-jobs. """
    if local:
        for seq_jobs in jobs.values():
            for job in seq_jobs:
                madx.resolve_and_run_file(job, log_file="{}.log".format(job), cwd=cwd)

    else:
        for idx_job, key in enumerate(jobs):
            LOG.info("Sending Job No. {:d}/{:d}.".format(idx_job + 1, len(jobs)))
            # create one folder per job to not get conflicts with the temp-subfolder
            job_dir = get_job_dir(cwd, key)
            bash = htc.write_madx_bash(job_dir, "", jobs[key])
            condor_job = htc.create_job_for_bashfile(bash, duration=max_duration)
            condor_sub = htc.create_subfile_from_job(job_dir, condor_job)
            htc.submit_jobfile(condor_sub)


# File Management ##############################################################


def get_nameparts_from_parameters(beam=None, xing=None, error_types=None, error_loc=None,
                                  seed=None, optic_type=None, ampdet=None):
    """ Creates strings from the parameters to be used in names """
    parts = []

    if seed is not None:
        parts.append("seed_{:04d}".format(seed))

    if beam is not None:
        parts.append("b{:d}".format(beam))

    if optic_type is not None:
        parts.append(optic_type)

    if error_types is not None:
        parts.append("errors_{:s}".format("_".join(error_types)))

    if error_loc is not None:
        parts.append("in_all_IPs" if "ALL" == error_loc else "in_{:s}".format(error_loc))

    if xing is not None:
        xing_map = {
            True: "wXing",
            False: "noXing",
            "else": "wXing_in_{:s}",
        }
        try:
            parts.append(xing_map[xing])
        except (TypeError, KeyError):
            parts.append(xing_map["else"].format("_".join(xing)))

    if ampdet is not None:
        parts.append(ampdet)
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
    seed_dir = os.path.join(cwd, "results_per_seed", get_nameparts_from_parameters(seed=seed)[0])
    iotools.create_dirs(seed_dir)
    return seed_dir


def get_job_dir(cwd, id):
    """ Build the job-dir-name and create it. """
    job_dir = os.path.join(cwd, "jobs", id)
    iotools.create_dirs(job_dir)
    return job_dir


def get_job_name(beam, xing, error_types, error_loc, seed):
    """ Return the name for the job """
    return ".".join(["job"] + get_nameparts_from_parameters(
        beam=beam, xing=xing, error_types=error_types, error_loc=error_loc, seed=seed
    ))


def get_errordef_path(path, errordef_mask, seed, error_loc):
    """ Return the fullpath to the error definition file """
    error_loc = "" if "ALL" == error_loc else ".{:s}".format(error_loc)
    try:
        return os.path.join(path, errordef_mask.format(seed=seed, loc=error_loc))
    except KeyError:
        if error_loc != "":
            raise KeyError("Error location given but no placeholder in wise-mask found!")
        return os.path.join(path, errordef_mask.format(seed=seed))


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


def check_opt(opt):
    """ Check the opt structure """
    if opt.error_locations is None:
        opt.error_locations = ["ALL"]
    return opt


# Script Mode ##################################################################


if __name__ == '__main__':
    # main()
    # main(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingOnOff")
    # main(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingIP1")
    # main(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="XingIP5")
    # main(entry_cfg="./irnl18_triplet_correction_configs/rdt_study.ini", section="B1XingOnOff")
    # main(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrorsXingTest")
    # main(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="OnlySextupoles")
    # main(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="OnlyHighpoles")
    # main(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrorsXing255")
    # main(entry_cfg="./irnl18_triplet_correction_configs/hllhc_ampdet_study.ini", section="AllErrorsOffDisp")
    # main(entry_cfg="./irnl18_triplet_correction_configs/ampdet_study.ini", section="All")
    # main(entry_cfg="./irnl18_triplet_correction_configs/md3311.ini", section="ErrorCheck")
#     main(entry_cfg="./irnl18_triplet_correction_configs/md3311.ini", section="FlatOrbit")
    main(entry_cfg="./irnl18_triplet_correction_configs/md3311.ini", section="CrossingIP5")
    main(entry_cfg="./irnl18_triplet_correction_configs/md3311.ini", section="NotCrossingIP5")
