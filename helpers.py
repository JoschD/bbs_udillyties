import os
import re
import sys
import random
import shutil

import matplotlib.pyplot as plt
import numpy as np
import pandas.core.indexes
import pandas
import seaborn

from utils import logging_tools
from tfs_files import tfs_pandas as tfs

LOG = logging_tools.get_logger(__name__)


# Renaming ###################################################################


def replace_pattern_in_filenames_by_str(folder, pattern, replace, filter=None, recursive=False, test=False):
    """ Rename files in `folder` by replacing the `pattern` with `replace`

    Args:
        folder: folder to search in for files to rename
        pattern: pattern to replace
        replace: string to replace it with
        filter: filter files by this first
        recursive: do it recursively
    """

    regex = re.compile(pattern)
    if filter:
        filter = re.compile(filter)

    for root, dirs, files in os.walk(folder):
        for file in files:
            if ((filter and filter.search(file)) or filter is None) and regex.search(file):
                src = os.path.join(root, file)
                dst = os.path.join(root, regex.sub(replace, file))
                LOG.info("'{}' -> '{}'".format(src, dst))
                if not test:
                    shutil.move(src, dst)
        if not recursive:
            break


# Entry Point ################################################################


def create_param_help_example():
    import amplitude_detuning_analysis
    create_param_help = CreateParamHelp()
    create_param_help(amplitude_detuning_analysis, "_get_plot_params")
    # create_param_help(amplitude_detuning_analysis)


class CreateParamHelp(object):
    """ Print params help quickly """
    def __init__(self):
        logging_tools.getLogger("").handlers = []  # remove all handlers from root-logger
        logging_tools.get_logger("__main__", fmt="%(message)s")  # set up new

    def __call__(self, module, param_fun=None):
        if param_fun is None:
            try:
                module.get_params().help()
            except AttributeError:
                module._get_params().help()
        else:
            getattr(module, param_fun)().help()

# TFS Manipulation ###########################################################


def filter_tfs(path_in, regex, path_out=None, case=True):
    """ Read tfs file and filter with regex by name """
    if path_out is None:
        path_out = path_in

    df = tfs.read_tfs(path_in, index="NAME")
    filter_idx_mask = df.index.str.contains(regex, case=case)
    tfs.write_tfs(path_out, df.loc[filter_idx_mask, :], save_index="NAME")


def convert_old_pandas_pickle(files):
    """ Opens old pandas pickles and saves them into new files"""
    sys.modules['pandas.indexes'] = pandas.core.indexes
    for f in files:
        df = pandas.read_pickle(f)
        pandas.to_pickle(df, os.path.join(f.replace(".dat", ".panda")))


# Maths ######################################################################


def get_random_cutoff_gauss(exp, n_sigma=2):
    """ Returns a random strength "gaussian" around 10**exp)

    "gaussian" means that mu=10**exp and sigma=.1*10**exp,
     but the tails are cut of at n_sigma * sigma.
    """
    mu = 10 ** exp
    sigma = .1 * mu
    s_min = mu - n_sigma*sigma
    s_max = mu + n_sigma*sigma
    while True:
        val = (random_sign() * random.gauss(mu, sigma))
        if s_min <= np.abs(val) <= s_max:
            return val


def random_sign():
    """ Returns +1 or -1 with 50:50 chances """
    return np.sign(random.random() - .5)


# Usage Examples #############################################################


def example_get_random_cutoff_gauss():
    seaborn.set(color_codes=True)
    x = []
    for i in range(1000):
        x.append(get_random_cutoff_gauss(-5))
    seaborn.distplot(x)
    plt.show()


def example_filter_tfs():
    folder = "/media/jdilly/Storage/PHD/2018_04_prelim_flatoptics_correction/30_error_origin_test/"
    all_errors = os.path.join(folder, "LHCsqueeze-0.4_10.0_0.4_3.0-6.5TeV-emfqcs-1.tfs")
    ip1_only = os.path.join(folder, "LHCsqueeze-0.4_10.0_0.4_3.0-6.5TeV-emfqcs-1-ip1.tfs")
    ip5_only = os.path.join(folder, "LHCsqueeze-0.4_10.0_0.4_3.0-6.5TeV-emfqcs-1-ip5.tfs")

    re_ip1 = r"^[^.]+\..*?(?<=[RL]1)(\.V[12])?"
    re_ip5 = r"^[^.]+\..*?(?<=[RL]5)(\.V[12])?"

    filter_tfs(all_errors, re_ip1, ip1_only)
    filter_tfs(all_errors, re_ip5, ip5_only)


# Script Mode ################################################################


if __name__ == '__main__':
    # replace_pattern_in_filenames_by_str("/home/jdilly/link_afs_work/private/STUDY.18.ampdet_flatoptics", "by_by_", "by_", recursive=True)
    # example_get_random_cutoff_gauss()
    create_param_help_example()
    pass