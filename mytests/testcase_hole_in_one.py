import os
import sys
from os.path import join
# Root of Beta-Beat.src
BB_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       os.path.pardir, os.path.pardir))
if BB_ROOT not in sys.path:
    sys.path.append(BB_ROOT)

from hole_in_one.hole_in_one import run_all
from hole_in_one.io_handlers.input_handler import parse_args
from utils import iotools


REGR_DIR = join(BB_ROOT, "tests", "regression")
TBTS = join(BB_ROOT, "tests", "inputs", "tbt_files")
MODELS = join(BB_ROOT, "tests", "inputs", "models")


if __name__ == '__main__':
    output_dir = join(REGR_DIR, "_out_hole_in_one_test_flat_3dkick")
    arguments = ("--file={file} --model={model} --output={output} clean "
                 "harpy --tunex 0.27 --tuney 0.322 --tunez 4.5e-4 "
                 "--nattunex 0.28 --nattuney 0.31".format(
        file=join(TBTS, "flat_beam1_3d.sdds"),
        model=join(MODELS, "flat_beam1", "twiss.dat"),
        output=output_dir)
    )

    iotools.create_dirs(output_dir)

    try:
        parsed_args = parse_args(arguments.split())
        run_all(*parsed_args)
    finally:
        iotools.delete_item(output_dir)
