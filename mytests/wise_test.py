import os
from tfs_files import tfs_pandas as tfs
from utils import iotools
from utils.entrypoint import entrypoint
from matplotlib import pyplot as plt
from matplotlib import colors
from plotshop import plot_style as ps
import seaborn as sns
import numpy as np
from utils import logging_tools

LOG = logging_tools.get_logger(__name__)


def _load_data(out_dir, magnets, order):
    return tfs.read_tfs(_get_filepath(out_dir, magnets, order) + ".tfs", index="NAME")


def _gather_data(wise_dir, wise_mask, magnets, order, seeds):
    df = tfs.TfsDataFrame(index=magnets, columns=seeds)
    for seed in seeds:
        LOG.info("Seed {:d} of {:d}".format(seed, len(seeds)))
        data_df = tfs.read_tfs(os.path.join(wise_dir, wise_mask.format(seed)), index="NAME")
        df.loc[:, seed] = data_df.loc[magnets, order]
    df.headers["MAGNETS"] = ", ".join(magnets)
    df.headers["ORDER"] = order
    df = df.rename(columns=str)
    return df


def _plot_hist(df):
    ps.set_style("standard")
    fig = plt.figure()
    ax = fig.gca()

    for idx, magnet in enumerate(df.index):
        c = ps.get_mpl_color(idx)
        ax.hist(df.loc[magnet, :], label="__nolegend__", color=colors.to_rgba(c, .2), density=True)
        ax.hist(df.loc[magnet, :], label=magnet, histtype="step", color=c, density=True)
        try:
            sns.kdeplot(df.loc[magnet, :], ax=ax, label="__nolegend__", color=c,
                        linestyle="--", marker="",)
        except np.linalg.linalg.LinAlgError:
            pass

    ps.make_top_legend(ax, ncol=3)
    ax.set_xlabel("{} Value".format(df.ORDER))
    ax.set_ylabel("Density")

    return fig


def _save(out_dir, df, fig):
    iotools.create_dirs(out_dir)
    path = _get_filepath(out_dir, df.MAGNETS, df.ORDER)

    tfs.write_tfs(path + ".tfs", df, save_index="NAME")

    fig.tight_layout()
    fig.savefig(path + ".png")
    fig.savefig(path + ".pdf")


def _get_filepath(out_dir, magnets, order):
    if isinstance(magnets, list):
        magnets = magnets[0]
    filename = "allWISE_{}_{}".format(magnets[:4], order)
    return os.path.join(out_dir, filename)


def get_params():
    return {
        "magnet_groups": dict(
            flags="--magnets", nargs='+', type=list, default=[]),
        "orders": dict(
            flags="--orders", nargs='+', type=str, default=[]),
        "wise_dir": dict(
            flags="--wise", type=str, required=True),
        "wise_mask": dict(
            flags="--mask", type=str, required=True),
        "out_dir": dict(
            flags="--outdir", type=str, default="."),
        "seeds": dict(
            flags="--seeds", type=int, nargs="+", default=range(1, 16)),
        "load_data": dict(
            flags="--load", action="store_true"),
    }


@entrypoint(get_params(), strict=True)
def main(opt):
    for magnets in opt.magnet_groups:
        for order in opt.orders:
            LOG.info("Loading '{}' with order '{}'".format(magnets, order))
            if opt.load_data:
                df = _load_data(opt.out_dir, magnets, order)
            else:
                df = _gather_data(opt.wise_dir, opt.wise_mask, magnets, order, opt.seeds)
            fig = _plot_hist(df)
            _save(opt.out_dir, df, fig)


if __name__ == '__main__':
    # main(entry_cfg="wise_test.ini", section="AfsWiseInjection")
    # main(entry_cfg="wise_test.ini", section="AfsWiseCollision")
    main(entry_cfg="wise_test.ini", section="MyWise")
