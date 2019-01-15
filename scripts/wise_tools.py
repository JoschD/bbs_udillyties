""" Tools for modifying WISE errortables. """

import os
import shutil

from utils import logging_tools
from tfs_files import tfs_pandas as tfs

LOG = logging_tools.get_logger(__name__)

EXT = ".tfs"
ERRORDEF_FILENAME = "WISE.errordef.{seed:04d}" + EXT


def filter_by_ip(ip, file_in, file_out):
    """ Filter the Error table by IP

    Args:
        ip (str): IPs to keep, e.g. "1" or "15" (filters IP1 and IP5)
        file_in: path to input error def file
        file_out: path to output file

    """
    df = tfs.read_tfs(file_in, index="NAME")
    mask = df.index.str.match(r".*[LR][{:s}](\.V[12])?".format(ip), case=False)
    tfs.write_tfs(file_out, df.loc[mask, :], save_index="NAME")


def filter_all_in_folder_by_ips(path_to_dir, ips, ext=EXT):
    """ Filter all files in a folder by the ips specified. """
    LOG.info("Filtering file in directory '{:s}'".format(path_to_dir))
    for file_in in os.listdir(path_to_dir):
        if file_in.endswith(ext):
            for ip in ips:
                ip = str(ip)
                file_out = "{:s}.IP{:s}{:s}".format(file_in[:-len(ext)], ip, ext)
                LOG.info("    Extracting '{:s}' -> '{:s}'.".format(file_in, file_out))
                full_file_in = os.path.join(path_to_dir, file_in)
                full_file_out = os.path.join(path_to_dir, file_out)
                filter_by_ip(ip, full_file_in, full_file_out)


def rename_files(path_to_dir, name_mask=ERRORDEF_FILENAME, dir_prefix=""):
    """ Rename the dir containing wise files so they all have the same standard.

    Beware that also the folder is renamed!
    If you give a fileextentsion with the `name_mask`, this one is assumed to be the one
    of the original files as well. Otherwise '.tfs' is assumed.
    The `name_mask` also needs to contain a format string named `seed` of integer type.

    Args:
        path_to_dir (str): Path to the directory containing wise-tfs files
        name_mask (str): new mask for naming the files, must contain {seed:d} or similar.


    """
    LOG.info("Accessing directory '{:s}'".format(path_to_dir))

    ext = os.path.splitext(name_mask)[1]
    ext = EXT if "" == ext else ext

    folder_out = None
    for file_in in os.listdir(path_to_dir):
        if file_in.endswith(ext):
            file_parts = file_in.split("-")
            if folder_out is None:
                folder_out = "-".join(file_parts[:-1])
            seed = int(file_parts[-1][:-len(ext)])
            file_out = name_mask.format(seed=seed)
            LOG.info("    Renaming '{:s}' to '{:s}'.".format(file_in, file_out))
            full_file_in = os.path.join(path_to_dir, file_in)
            full_file_out = os.path.join(path_to_dir, file_out)
            shutil.move(full_file_in, full_file_out)

    folder_out = os.path.abspath(os.path.join(path_to_dir, os.path.pardir, dir_prefix + folder_out))
    LOG.info("Renaming dir '{:s}' to '{:s}'.".format(path_to_dir, folder_out))
    shutil.move(path_to_dir, folder_out)
    return folder_out


# Script Mode ##################################################################


if __name__ == '__main__':
    raise EnvironmentError("{:s} is not supposed to run as main.".format(__file__))

