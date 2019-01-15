import matplotlib
from plotshop import plot_style as ps
from matplotlib import pyplot as plt

if __name__ == '__main__':
    ps.set_style("standard", {
        u"ps.usedistiller": u"xpdf",
        u"pdf.compression": 9,
    })
    fig = plt.figure()
    ax = fig.gca()
    ax.plot(range(10))
    plt.show()

    fig.savefig("testfig.pdf")
