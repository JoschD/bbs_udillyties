import os
import sys
import random

import matplotlib.pyplot as plt
import numpy as np
import pandas.core.indexes
import pandas
import seaborn

from utils import logging_tools
from utils import tfs_pandas as tfs


# Entry Point ################################################################


def create_param_help_example():
    import global_correct_iterative
    create_param_help = CreateParamHelp()
    create_param_help(global_correct_iterative)


class CreateParamHelp(object):
    """ Print params help quickly """
    def __init__(self):
        logging_tools.get_logger("__main__", fmt="%(message)s")

    def __call__(self, module):
        try:
            module.get_params().help()
        except AttributeError:
            module._get_params().help()


# TFS Manipulation ###########################################################


def filter_tfs(path_in, regex, path_out=None):
    """ Read tfs file and filter with regex by name """
    if path_out is None:
        path_out = path_in

    df = tfs.read_tfs(path_in, index="NAME")
    filter_idx = tfs.get_index_by_regex(df, regex)
    tfs.write_tfs(path_out, df.loc[filter_idx, :], save_index="NAME")


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
    example_get_random_cutoff_gauss()