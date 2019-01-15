import os
import sys

# Root of Beta-Beat.src
BB_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       os.path.pardir, os.path.pardir))
if BB_ROOT not in sys.path:
    sys.path.append(BB_ROOT)

from twiss_optics import optics_class
from tfs_files import tfs_pandas as tfs
from utils import logging_tools

LOG = logging_tools.get_logger(__name__, level_console=0)

def rdt_test():
    model_path = os.path.join(BB_ROOT, "udillyties", "inputs", "twiss_2sext_elements.dat")
    data_frame = tfs.read_tfs(model_path, index="NAME")

    data_frame = data_frame.loc[data_frame.index.str.match("M|B")]

    twiss_opt = optics_class.TwissOptics(data_frame)

    twiss_opt.calc_rdts(["F1002", "F1020", "F2100"])
    twiss_opt.plot_rdts(["F1002", "F1020", "F2100"])


def michi_test():
    test_df = tfs.read_tfs("twiss_skew.tfs", index='NAME')
    test_class = optics_class.TwissOptics(test_df)
    # test_class.get_coupling(method="cmatrix")
    coupling_rdts = test_class.get_rdts(rdt_names=['F1010', 'F1001'])

if __name__ == '__main__':
    michi_test()
    # rdt_test()
