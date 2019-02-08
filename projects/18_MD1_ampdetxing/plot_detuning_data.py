import tune_analysis.kickac_modifiers
from tune_analysis import constants as ta_const
from matplotlib import pyplot as plt
from matplotlib import colors
from collections import OrderedDict
from tfs_files import tfs_pandas
from plotshop import plot_style

BASE_DIR = "/media/jdilly/Storage/Projects/NOTE.18.MD3311.Amplitude_Detuning/results.md_note/results/"
OUT_DIR = "/media/jdilly/Storage/Projects/NOTE.18.MD3311.Amplitude_Detuning/results.180128.for_omc/results/"
# PRES_MODE = True
OUT_DIR = BASE_DIR
PRES_MODE = False

DATA = {
    "plot.2018.b1.hkicks.full.flat.ip5xing": OrderedDict([
        ("B1 H-Kicks Flat-Orbit", BASE_DIR + "beam1/B1_flatorbit_H/getkickac_ampdet.out"),
        ("B1 H-Kicks IP5 X'ing", BASE_DIR + "beam1/B1_flatorbit_IP5xing_H/getkickac_ampdet.out"),
        ("B1 H-Kicks Full X'ing", BASE_DIR + "2018_commissioning/getkickac_ampdet.out"),
        ]),
    "plot.2018.b1.hkicks.flat.ip5xing": OrderedDict([
            ("B1 H-Kicks Flat-Orbit", BASE_DIR + "beam1/B1_flatorbit_H/getkickac_ampdet.out"),
            ("B1 H-Kicks IP5 X'ing", BASE_DIR + "beam1/B1_flatorbit_IP5xing_H/getkickac_ampdet.out"),
        ]),
    "plot.2018.b1.vkicks.flat.ip5xing": OrderedDict([
        ("B1 V-Kicks Flat-Orbit", BASE_DIR + "beam1/B1_flatorbit_V_Qshift/getkickac_ampdet.out"),
        ("B1 V-Kicks IP5 X'ing", BASE_DIR + "beam1/B1_flatorbit_IP5xing_V_Qshift/getkickac_ampdet.out"),
    ]),
    "plot.2018.b2.hkicks.flat.ip5xing": OrderedDict([
        ("B2 H-Kicks Flat-Orbit", BASE_DIR + "beam2/B2_flatorbit_H/getkickac_ampdet.out"),
        ("B2 H-Kicks IP5 X'ing", BASE_DIR + "beam2/B2_flatorbit_IP5xing_H/getkickac_ampdet.out"),
    ]),
    "plot.2018.b2.vkicks.flat.ip5xing": OrderedDict([
        ("B2 V-Kicks Flat-Orbit", BASE_DIR + "beam2/B2_flatorbit_V/getkickac_ampdet.out"),
        ("B2 V-Kicks IP5 X'ing", BASE_DIR + "beam2/B2_flatorbit_IP5xing_V/getkickac_ampdet.out"),
    ]),
}


if __name__ == '__main__':
    plot_style.set_style("standard")
    pres_label = ""
    if PRES_MODE:
        plot_style.set_style("presentation")
        pres_label = "pres."
    for data_key in DATA.keys():
        data = DATA[data_key]
        df = OrderedDict()
        action_plane = "X" if "hkicks" in data_key else "Y"
        for key in data.keys():
            df[key] = tfs_pandas.read_tfs(data[key])

        for tune_plane in "XY":
            if not PRES_MODE:
                fig = plt.figure(figsize=[8, 6.5])
            else:
                fig = plt.figure(figsize=[10, 10])
            ax = fig.gca()
            for idx, key in enumerate(df.keys()):
                plot_data = tune_analysis.kickac_modifiers.get_ampdet_data(df[key],
                                                                           action_plane,
                                                                           tune_plane,
                                                                           corrected=True,
                                                                           )
                plot_data["label"] = key
                plot_data["color"] = plot_style.get_mpl_color(idx)

                plot_odr = tune_analysis.kickac_modifiers.get_odr_data(df[key],
                                                                       action_plane,
                                                                       tune_plane,
                                                                       corrected=True)
                plot_data["y"] -= plot_odr.pop("offset")

                # plot_data["y"] *= 1E3

                plot_data["linestyle"] = ""
                plot_data["marker"] = "o"

                plot_odr["marker"] = ""
                plot_odr["linestyle"] = "--"
                plot_odr["color"] = colors.to_rgba(plot_data["color"], .8)
                # plot_odr["y"] *= 1E3

                ax.fill_between(plot_odr["x"], plot_odr.pop("ylower"), plot_odr.pop("yupper"),
                                facecolor=plot_odr["color"][:3] + (.3,))

                ax.errorbar(**plot_data)
                ax.plot(plot_odr.pop("x"), plot_odr.pop("y"), **plot_odr)

                ax.set_xlim([0, 0.017])
                ax.set_ylim([-.0012, 0.0014])
            plot_style.make_top_legend(ax, 2)
            ax.set_yticks([-1e-3, -.5e-3, 0, .5e-3, 1e-3])
            plot_style.set_sci_magnitude(ax, axis="y", order=-3, fformat="%3.2f")
            plot_style.set_sci_magnitude(ax, axis="x", order=0, fformat="%0.3f")
            if PRES_MODE:
                plot_style.set_sci_magnitude(ax, axis="x", order=-3, fformat="%2.0f")
            # ax.ticklabel_format(style="sci", useMathText=True, scilimits=(-3, -3))
            labels = ta_const.get_paired_lables(action_plane, tune_plane)
            ax.set_xlabel(labels[0])
            ax.set_ylabel(labels[1])
            fig.tight_layout()
            # fig.tight_layout()

            fig_name = "{:s}{:s}.J{:s}Q{:s}.pdf".format(pres_label, data_key,
                                                        action_plane, tune_plane)
            fig.savefig(OUT_DIR + fig_name)
    plt.show()

