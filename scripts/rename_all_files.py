from udillyties import helpers
from utils import logging_tools

LOG = logging_tools.get_logger(__name__)

if __name__ == '__main__':
    helpers.replace_pattern_in_filenames_by_str(
        "/home/jdilly/link_afs_work/private/STUDY.18.ampdet_flatoptics/results_per_seed",
        pattern=r"\.all_errors\.",
        replace=".errors_all.",
        recursive=True,)