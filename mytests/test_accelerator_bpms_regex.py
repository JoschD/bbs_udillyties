import pandas as pd
import numpy as np
import re
from tfs_files import tfs_pandas as tfs
import timeit


def get_arc_bpms_mask_old(list_of_elements):
    mask = []
    pattern = re.compile(r"BPM.*\.([0-9]+)[RL].\..*", re.IGNORECASE)
    for element in list_of_elements:
        match = pattern.match(element)
        # The arc bpms are from BPM.14... and up
        if match and int(match.group(1)) > 14:
            mask.append(True)
        else:
            mask.append(False)
    return np.array(mask)


def get_arc_bpms_mask_a(bpm_names):
    """ Returns a boolean array for all bpms >14 L or R of IPs in bpm_names. """
    return pd.Series(bpm_names).str.match(r"BPM.*\.0*(1[5-9]|[2-9]\d|[1-9]\d{2,})[RL]",
                                          case=False).values


def get_arc_bpms_mask_b(bpm_names):
    """ Returns a boolean array for all bpms >14 L or R of IPs in bpm_names. """
    pattern = re.compile(r"BPM.*\.0*(1[5-9]|[2-9]\d|[1-9]\d{2,})[RL].\..*", re.IGNORECASE)
    return np.array([pattern.match(element) is not None for element in bpm_names])


def get_arc_bpms_mask_c(bpm_names):
    """ Returns a boolean array for all bpms >14 L or R of IPs in bpm_names. """
    mask = np.zeros(len(bpm_names), dtype=bool)
    pattern = re.compile(r"BPM.*\.0*(1[5-9]|[2-9]\d|[1-9]\d{2,})[RL].\..*", re.IGNORECASE)
    for idx, element in enumerate(bpm_names):
        if pattern.match(element):
            mask[idx] = True
    return mask


def lhc_test():
    names = tfs.read_tfs("tests/inputs/models/flat_beam1/twiss_elements.dat", index="NAME").index
    mask_old = get_arc_bpms_mask_old(names)
    mask_a = get_arc_bpms_mask_a(names)
    mask_b = get_arc_bpms_mask_b(names)
    mask_c = get_arc_bpms_mask_c(names)
    print "Differences old/a:" + ",".join(np.array(names)[mask_a != mask_old])
    print "Differences old/b:" + ",".join(np.array(names)[mask_b != mask_old])
    print "Differences old/c:" + ",".join(np.array(names)[mask_c != mask_old])
    n = 100
    print "old: {}s".format(timeit.timeit(lambda x=names: get_arc_bpms_mask_old(x), number=n))
    print "a: {}s".format(timeit.timeit(lambda x=names: get_arc_bpms_mask_a(x), number=n))
    print "b: {}s".format(timeit.timeit(lambda x=names: get_arc_bpms_mask_b(x), number=n))
    print "c: {}s".format(timeit.timeit(lambda x=names: get_arc_bpms_mask_c(x), number=n))


def get_arc_bpms_mask_esrf_a(list_of_elements):
    """ Chooses the bpms with large dispersion.
    Which are:
        bpms 1-5 in even cells.
        bpms 3-7 in odd cells. """
    return pd.Series(list_of_elements).str.match(
        r"BPM\.(\d*[02468]\.[1-5]|\d*[13579]\.[3-7])",
        case=False).values


def get_arc_bpms_mask_esrf_old(list_of_elements):
    mask = []
    pattern = re.compile("BPM\.([0-9]+)\.([1-7])", re.IGNORECASE)
    for element in list_of_elements:
        match = pattern.match(element)
        # The arc bpms are from BPM.14... and up
        if match:
            cell = int(match.group(1))
            bpm_number = int(match.group(2))
            mask.append(not ((cell % 2 == 0 and bpm_number in [6, 7]) or
                             (cell % 2 != 0 and bpm_number in [1, 2])))
        else:
            mask.append(False)
    return np.array(mask)


def esrf_test():
    names = ["BPM.{:d}.{:d}".format(cell, bpm) for cell in range(0, 100) for bpm in range(0, 9)]
    mask_old = get_arc_bpms_mask_esrf_old(names)
    mask_a = get_arc_bpms_mask_esrf_a(names)
    print "Differences old/a:" + ",".join(np.array(names)[mask_a != mask_old])

    n = 100
    print "old: {}s".format(timeit.timeit(lambda x=names: get_arc_bpms_mask_esrf_old(x), number=n))
    print "a: {}s".format(timeit.timeit(lambda x=names: get_arc_bpms_mask_esrf_a(x), number=n))



if __name__ == '__main__':
    lhc_test()
    # esrf_test()