from plotshop import plot_style as ps
from matplotlib.lines import Line2D
from matplotlib import pyplot as plt
from fractions import gcd


LOCATION_FONT_SIZE = 11
RESONANCE_LINES_TEXT_POS = (0.32, 0.935)  # position of the "Resonance Lines:" (None for deact.)
FIGURE_SIZE = [7, 7]
LEGEND_COLUMNS = 2
GRID_ALPHA = 0

LINE_STYLES = ["-", "-", "--", "--", ":"]


# Main Function ################################################################


def plot_locations(locations, order, qx_lim, qy_lim, outpath=None, show=False):
    """ Plot given locations into tune diagram.

    Args:
        locations: list of triplets of Qx, Qy and label
        order: max order of resonance lines to plot
        qx_lim: limits for qx
        qy_lim: limits for qy
        outpath: save data as tfs

    Returns:
        figure
    """
    ps.set_style("standard", {u"figure.figsize": FIGURE_SIZE, u"grid.alpha": GRID_ALPHA})
    fig, ax = plt.subplots(1, 1)

    # do resonances
    resonances = get_resonance_lines(order)
    for r in resonances:
        r.plot(ax)

    # do locations
    _plot_locations(ax, locations, qx_lim)

    # adjust axis
    ax.set_xlim(qx_lim)
    ax.set_ylim(qy_lim)
    ax.set_xlabel("$Q_x$")
    ax.set_ylabel("$Q_y$")
    _make_lines_legend(ax, order)

    if outpath:
        fig.savefig(outpath)

    if show:
        plt.show()
    return fig


# Resonance Lines ##############################################################


class Line(object):
    """ Used for storing line data and plotting. """
    def __init__(self, x, y, nx, ny, order=None):
        self.x = x
        self.y = y
        self.nx = nx
        self.ny = ny
        if order is None:
            order = abs(nx) + abs(ny)
        self.order = order

    def plot(self, ax):
        ax.plot(self.x, self.y,
                ls=_get_ls(self.order),
                marker="",
                c=_get_lc(self.order),
                label="({}, {})".format(self.nx, self.ny)
                )


def get_resonance_lines(max_order):
    """ Return a list of all resonance lines up to max_order. """
    lines = []
    max_range = max_order + 1
    for nx in range(-max_range, max_range):
        for ny in range(-max_range, max_range):
            div, order = gcd(nx, ny), abs(nx) + abs(ny)
            for p in range(-max_range, max_range):
                if any([p, nx, ny]) and order <= max_order and _not_a_multiple(nx, ny, p, div):
                    lim = _get_interval(nx, ny, p)
                    if lim is not None:
                        lines.append(Line(x=(0, 1), y=lim, nx=nx, ny=ny, order=order))

                    lim = _get_interval(ny, nx, p)
                    if lim is not None:
                        lines.append(Line(x=lim, y=(0, 1), nx=nx, ny=ny, order=order))

    return lines


def _not_a_multiple(nx, ny, p, div):
    """ Check if this line has a smaller set of nx, ny and p """
    if not div:  # nx and ny are zero
        return False

    if div == 1:  # either nx and/or ny are 1 or no common divisor
        return True
    if div == nx:  # ny is zero or multiple of nx
        return gcd(p, nx) == 1
    if div == ny:  # nx is zero or multiple of ny
        return gcd(p, ny) == 1

    # nx and ny are not zero & have common divisor -> check if p has same divisor
    p_frac = float(p) / div
    return int(p_frac) != p_frac


def _get_interval(na, nb, p):
    """ Returns _get_value in [0, 1] if na is not 0. """
    if not na:
        return None

    interval = [_get_value(na, nb, n, p) for n in [0, 1]]
    if all([0 <= l <= 1 for l in interval]):
        return interval

    return None


def _get_value(na, nb, qb, p):
    """ Returns Qa for given Qb. """
    return float((p-nb*qb))/na


# Plotting #####################################################################


def _get_ls(order):
    """ Return linestyle for order """
    try:
        return LINE_STYLES[order - 1]
    except IndexError:
        return LINE_STYLES[-1]


def _get_lc(order):
    """ Return line color for order """
    return ps.get_mpl_color(order-1)


def _get_tc(idx):
    """ Return the text color for the locations. """
    # return ps.get_mpl_color(idx)
    return "k"


def _make_lines_legend(ax, max_order):
    """ Create legend handles and labels for resonance orders """
    handles, labels = _empty_list(max_order+1), _empty_list(max_order+1)
    for idx in range(max_order):
        order = idx+1
        handles[idx] = Line2D([0], [0], c=_get_lc(order), ls=_get_ls(order))
        labels[idx] = "{}. order".format(order)

    ps.make_top_legend(ax, ncol=LEGEND_COLUMNS, handles=handles, labels=labels)
    if RESONANCE_LINES_TEXT_POS is not None:
        ax.text(RESONANCE_LINES_TEXT_POS[0], RESONANCE_LINES_TEXT_POS[1],
                "Resonance Lines:", ha="right", transform=ax.figure.transFigure)


def _plot_locations(ax, locations, qx_lim):
    """ Plots the locations. """
    txt_offset = (qx_lim[1] - qx_lim[0]) * 0.02
    for idx, l in enumerate(locations):
        c = _get_tc(idx)
        fsize = LOCATION_FONT_SIZE
        ax.plot(l[0], l[1], label=l[2], marker="x", color=c)
        ax.text(l[0] + txt_offset, l[1], "({:}, {:})".format(l[0], l[1]),
                color=c, fontsize=fsize, va="top", ha="left")
        ax.text(l[0] + txt_offset, l[1], l[2],
                color=c, fontsize=fsize, va="bottom", ha="left")


# Helper #######################################################################


def _empty_list(l):
    """ Return an empty list of length l. """
    return [None] * l


if __name__ == '__main__':
    # main([], 7, [0, 1], [0, 1], show=True)
    plot_locations([(.28, .31, "Injection"),
                    (.31, .32, "Collision"),
                    (.305, .325, "Probe")],
                   order=6,
                   qx_lim=[.26, .34], qy_lim=[.26, .34],
                   outpath="/media/jdilly/Storage/Projects/NOTE.18.MD3311.Amplitude_Detuning/results.md_note/results/rdt_analysis/tune_diag.pdf",
                   show=False)
