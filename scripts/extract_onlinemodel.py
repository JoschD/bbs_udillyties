from online_model import extractor_wrapper
from utils import iotools
from utils import logging_tools

from extract_online_model import main
# LOG = logging_tools.get_logger(__name__, level_console=logging_tools.DEBUG)
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

TIME = "2018-10-30 15:00:00.000"
CWD = "/afs/cern.ch/user/j/jdilly/extractHLLHCDA/"


def main1(knob_names=KNOB_NAMES, time=TIME, root_cwd=CWD):
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
    main(function="overview", time=TIME, cwd=os.path.join(CWD, "entrypointtest"), server="cs-ccr-dev3")


def hllhcda():
    main(function="overview",
         time="2018-10-30 16:15:00.000",
         cwd="/afs/cern.ch/user/j/jdilly/extractHLLHCDA/",
         server="cs-ccr-dev3",
         knob_names=[
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
             # "LHCBEAM/IP8-SEP-H-MM",

             # "LHCBEAM/IP5-OFFSET-V-MM",

             "LHCBEAM/2018_global_ats_flat_b1_for_ip5_waist",
             "LHCBEAM/2018_MD4_replicatingHL_a3",
             "LHCBEAM/2018_MD4_replicatingHL_b3",
             "LHCBEAM/2018_MD4_replicatingHL_a4",
             "LHCBEAM/2018_MD4_replicatingHL_b4",
             "LHCBEAM/2018_MD4_replicatingHL_b6",
         ],
         )


def ampdet_commish_2018():
    main(function="overview",
         time="2018-04-28 15:00:00.000",
         cwd="/afs/cern.ch/user/j/jdilly/extract_temp/",
         server="cs-ccr-dev3",
         knob_names=[
             "LHCBEAM/IP1-XING-H-MURAD",
             "LHCBEAM/IP1-XING-V-MURAD",
             "LHCBEAM/IP2-XING-V-MURAD",
             "LHCBEAM/IP5-XING-H-MURAD",
             "LHCBEAM/IP5-XING-V-MURAD",
             "LHCBEAM/IP8-XING-H-MURAD",

             "LHCBEAM/IP1-SEP-H-MM",
             "LHCBEAM/IP1-SEP-V-MM",
             "LHCBEAM/IP2-SEP-H-MM",
             "LHCBEAM/IP5-SEP-H-MM",
             "LHCBEAM/IP5-SEP-V-MM",
             "LHCBEAM/IP8-SEP-V-MM",

             "LHCBEAM/IP5-OFFSET-V-MM",
         ],
         )


def ampdet_md3311_2018():
    main(function="overview",
         time="2018-06-16 21:00:00.000",
         cwd="/afs/cern.ch/user/j/jdilly/extract_temp/",
         server="cs-ccr-dev3",
         knob_names=[
             "LHCBEAM/IP1-XING-H-MURAD",
             "LHCBEAM/IP1-XING-V-MURAD",
             "LHCBEAM/IP2-XING-V-MURAD",
             "LHCBEAM/IP5-XING-H-MURAD",
             "LHCBEAM/IP5-XING-V-MURAD",
             "LHCBEAM/IP8-XING-H-MURAD",

             "LHCBEAM/IP1-SEP-H-MM",
             "LHCBEAM/IP1-SEP-V-MM",
             "LHCBEAM/IP2-SEP-H-MM",
             "LHCBEAM/IP5-SEP-H-MM",
             "LHCBEAM/IP5-SEP-V-MM",
             "LHCBEAM/IP8-SEP-V-MM",

             "LHCBEAM/IP5-OFFSET-V-MM",
         ],
         )


def kmod_md3311_2018():
    main(function="overview",
         time="2018-06-16 15:48:00.000",
         cwd="/afs/cern.ch/user/j/jdilly/extract_temp/",
         server="cs-ccr-dev3",
         knob_names=[
             "LHCBEAM/IP1-XING-H-MURAD",
             "LHCBEAM/IP1-XING-V-MURAD",
             "LHCBEAM/IP2-XING-V-MURAD",
             "LHCBEAM/IP5-XING-H-MURAD",
             "LHCBEAM/IP5-XING-V-MURAD",
             "LHCBEAM/IP8-XING-H-MURAD",

             "LHCBEAM/IP1-SEP-H-MM",
             "LHCBEAM/IP1-SEP-V-MM",
             "LHCBEAM/IP2-SEP-H-MM",
             "LHCBEAM/IP5-SEP-H-MM",
             "LHCBEAM/IP5-SEP-V-MM",
             "LHCBEAM/IP8-SEP-V-MM",

             "LHCBEAM/IP5-OFFSET-V-MM",
         ],
         )

def kmod_commish_2018_04_11():
    main(function="overview",
         time="2018-04-10 23:12:00.000",
         cwd="/afs/cern.ch/user/j/jdilly/extract_temp/",
         server="cs-ccr-dev3",
         knob_names=[
             "LHCBEAM/IP1-XING-H-MURAD",
             "LHCBEAM/IP1-XING-V-MURAD",
             "LHCBEAM/IP2-XING-V-MURAD",
             "LHCBEAM/IP5-XING-H-MURAD",
             "LHCBEAM/IP5-XING-V-MURAD",
             "LHCBEAM/IP8-XING-H-MURAD",

             "LHCBEAM/IP1-SEP-H-MM",
             "LHCBEAM/IP1-SEP-V-MM",
             "LHCBEAM/IP2-SEP-H-MM",
             "LHCBEAM/IP5-SEP-H-MM",
             "LHCBEAM/IP5-SEP-V-MM",
             "LHCBEAM/IP8-SEP-V-MM",

             "LHCBEAM/IP5-OFFSET-V-MM",
         ],
         )

if __name__ == '__main__':
    kmod_commish_2018_04_11()

