from online_model import extractor_wrapper
from utils import iotools
from utils import logging_tools

LOG = logging_tools.get_logger(__name__)

import os

KNOB_NAMES = (
    "LHCBEAM/IP1-XING-H-MURAD",
    "LHCBEAM/IP1-XING-V-MURAD",
    "LHCBEAM/IP2-XING-V-MURAD",
    "LHCBEAM/IP5-XING-H-MURAD",
    "LHCBEAM/IP5-XING-V-MURAD",
    "LHCBEAM/IP8-XING-H-MURAD",

    "LHCBEAM/IP1-SEP-H-MM",
    "LHCBEAM/IP1-SEP-V-MM",
    "LHCBEAM/IP2-SEP-H-MM",
    # "LHCBEAM/IP2-SEP-V-MM",
    "LHCBEAM/IP5-SEP-H-MM",
    "LHCBEAM/IP5-SEP-V-MM",
    "LHCBEAM/IP8-SEP-V-MM",

    # "LHCBEAM/IP1-OFFSET-H-MM",
    # "LHCBEAM/IP1-OFFSET-V-MM",
    # "LHCBEAM/IP2-OFFSET-V-2MM",
    # "LHCBEAM/IP2-OFFSET-V-MM",
    # "LHCBEAM/IP5-OFFSET-H-MM",
    "LHCBEAM/IP5-OFFSET-V-MM",
    # "LHCBEAM/IP8-OFFSET-H-MM",
)

# KNOB_NAMES = (
#     "LHCBEAM/IP1-SEP-H-MM",
#     "LHCBEAM/IP1-OFFSET-H-MM",
# )

TIME = "2018-06-16 15:30:00.000"
CWD = "/afs/cern.ch/user/j/jdilly/extractor/"


def main(knob_names=KNOB_NAMES, time=TIME, root_cwd=CWD):
    for knob in knob_names:
        cwd = os.path.join(root_cwd, knob)
        iotools.create_dirs(cwd)
        try:
            extractor_wrapper.extract_knob_value_and_definition(knob, time, cwd, server="cs-ccr-dev3")
        except IOError:
            pass


def main2(knob_names=KNOB_NAMES, time=TIME, root_cwd=CWD):
    cwd = os.path.join(root_cwd, "newcode")
    iotools.create_dirs(cwd)
    try:
        extractor_wrapper.extract_knob_value_and_definition(knob_names, time, cwd, server="cs-ccr-dev3")
    except IOError:
        pass


def main3(knob_names=KNOB_NAMES, time=TIME, root_cwd=CWD):
    cwd = os.path.join(root_cwd, "overview")
    iotools.create_dirs(cwd)
    try:
        extractor_wrapper.extract_overview(knob_names, time, cwd, server="cs-ccr-dev3", show_plot=True)
    except IOError:
        pass


def main4():
    from extract_online_model import main
    main(function="overview", time=TIME, cwd=os.path.join(CWD, "entrypointtest"), server="cs-ccr-dev3")


if __name__ == '__main__':
    main4()

