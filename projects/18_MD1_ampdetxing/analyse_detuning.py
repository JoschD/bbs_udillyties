import amplitude_detuning_analysis as ampdet
from plotshop import post_processing
from figure_editor import main as figedit
from matplotlib import pyplot as plt

BASE_DIR = "/media/jdilly/Storage/Projects/NOTE.18.MD1_Amplitude_Detuning/overleaf/results/"
SHOW_PLOTS = False
XLIM = [0., 0.017]
YLIM = [-.001, 0.0008]


# Beam 2 #######################################################################


def get_new_plots_b2_y_ip5xing():
    sub_dir = "beam2/B2_flatorbit_IP5xing_V/"
    id = "plot.2018.b2.vkicks.ip5xing."
    setup = {
        "label": "B2 V-Kicks IP5 X'ing",
        "beam": 2,
        "plane": "Y",
        "kickac_path": BASE_DIR + sub_dir + "getkickac.out",
        "kickac_out": BASE_DIR + sub_dir + "getkickac_ampdet.out",
        "tune_x": 0.3105,
        "tune_y": 0.32,
        "window_length": 200,
        "tune_cut": 0.0005,
        "fine_window": 100,
        "fine_cut": 0.0001,
        "bbq_plot_out": BASE_DIR + id + "bbq.pdf",
        "ampdet_plot_out": BASE_DIR + id + "ampdet.pdf",
        "bbq_out": BASE_DIR + sub_dir + "bbq_ampdet.out",
        "bbq_plot_show": SHOW_PLOTS,
        "ampdet_plot_show": SHOW_PLOTS,
        "ampdet_plot_xmin": XLIM[0],
        "ampdet_plot_xmax": XLIM[1],
        "ampdet_plot_ymin": YLIM[0],
        "ampdet_plot_ymax": YLIM[1],
    }
    return ampdet.analyse_with_bbq_corrections(**setup)


def get_new_plots_b2_y_flat():
    sub_dir = "beam2/B2_flatorbit_V/"
    id = "plot.2018.b2.vkicks.flat."
    setup = {
        "label": "B2 V-Kicks Flat-Orbit",
        "beam": 2,
        "plane": "Y",
        "kickac_path": BASE_DIR + sub_dir + "getkickac.out",
        "kickac_out": BASE_DIR + sub_dir + "getkickac_ampdet.out",
        "tune_x": 0.31,
        "tune_y": 0.32,
        "window_length": 200,
        "tune_cut": 0.0005,
        "fine_window": 100,
        "fine_cut": 0.0001,
        "bbq_plot_out": BASE_DIR + id + "bbq.pdf",
        "ampdet_plot_out": BASE_DIR + id + "ampdet.pdf",
        "bbq_out": BASE_DIR + sub_dir + "bbq_ampdet.out",
        "bbq_plot_show": SHOW_PLOTS,
        "ampdet_plot_show": SHOW_PLOTS,
        "ampdet_plot_xmin": XLIM[0],
        "ampdet_plot_xmax": XLIM[1],
        "ampdet_plot_ymin": YLIM[0],
        "ampdet_plot_ymax": YLIM[1],
    }
    return ampdet.analyse_with_bbq_corrections(**setup)


def get_new_plots_b2_x_flat():
    sub_dir = "beam2/B2_flatorbit_H/"
    id = "plot.2018.b2.hkicks.flat."
    setup = {
        "label": "B2 H-Kicks Flat-Orbit",
        "beam": 2,
        "plane": "X",
        "kickac_path": BASE_DIR + sub_dir + "getkickac.out",
        "kickac_out": BASE_DIR + sub_dir + "getkickac_ampdet.out",
        "tune_x": 0.31,
        "tune_y": 0.32,
        "window_length": 200,
        "tune_cut": 0.0005,
        "fine_window": 100,
        "fine_cut": 0.0001,
        "bbq_plot_out": BASE_DIR + id + "bbq.pdf",
        "ampdet_plot_out": BASE_DIR + id + "ampdet.pdf",
        "bbq_out": BASE_DIR + sub_dir + "bbq_ampdet.out",
        "bbq_plot_show": SHOW_PLOTS,
        "ampdet_plot_show": SHOW_PLOTS,
        "ampdet_plot_xmin": XLIM[0],
        "ampdet_plot_xmax": XLIM[1],
        "ampdet_plot_ymin": YLIM[0],
        "ampdet_plot_ymax": YLIM[1],
    }
    return ampdet.analyse_with_bbq_corrections(**setup)


def get_new_plots_b2_x_ip5xing():
    sub_dir = "beam2/B2_flatorbit_IP5xing_H/"
    id = "plot.2018.b2.hkicks.ip5xing."
    setup = {
        "label": "B2 H-Kicks IP5 X'ing",
        "beam": 2,
        "plane": "X",
        "kickac_path": BASE_DIR + sub_dir + "getkickac.out",
        "kickac_out": BASE_DIR + sub_dir + "getkickac_ampdet.out",
        "tune_x": 0.31,
        "tune_y": 0.32,
        "window_length": 200,
        "tune_cut": 0.001,
        "fine_window": 100,
        "fine_cut": 0.0001,
        "bbq_plot_out": BASE_DIR + id + "bbq.pdf",
        "ampdet_plot_out": BASE_DIR + id + "ampdet.pdf",
        "bbq_plot_show": SHOW_PLOTS,
        "ampdet_plot_show": SHOW_PLOTS,
        "ampdet_plot_xmin": XLIM[0],
        "ampdet_plot_xmax": XLIM[1],
        "ampdet_plot_ymin": YLIM[0],
        "ampdet_plot_ymax": YLIM[1],
    }
    return ampdet.analyse_with_bbq_corrections(**setup)


# Beam 1 Qshift ################################################################


def get_new_plots_b1_y_ip5xing_qshift():
    sub_dir = "beam1/B1_flatorbit_IP5xing_V_Qshift/"
    id = "plot.2018.b1.vkicks.ip5xing.qshift."
    setup = {
        "label": "B1 V-Kicks IP5 X'ing QShift",
        "beam": 1,
        "plane": "Y",
        "kickac_path": BASE_DIR + sub_dir + "getkickac.out",
        "kickac_out": BASE_DIR + sub_dir + "getkickac_ampdet.out",
        "tune_x": 0.304,
        "tune_y": 0.315,
        "window_length": 200,
        "tune_cut": 0.0005,
        "fine_window": 100,
        "fine_cut": 0.0001,
        "bbq_plot_out": BASE_DIR + id + "bbq.pdf",
        "ampdet_plot_out": BASE_DIR + id + "ampdet.pdf",
        "bbq_out": BASE_DIR + sub_dir + "bbq_ampdet.out",
        "bbq_plot_show": SHOW_PLOTS,
        "ampdet_plot_show": SHOW_PLOTS,
        "ampdet_plot_xmin": XLIM[0],
        "ampdet_plot_xmax": XLIM[1],
        "ampdet_plot_ymin": YLIM[0],
        "ampdet_plot_ymax": YLIM[1],
    }
    return ampdet.analyse_with_bbq_corrections(**setup)


def get_new_plots_b1_y_flat_qshift():
    sub_dir = "beam1/B1_flatorbit_V_Qshift/"
    id = "plot.2018.b1.vkicks.flat.qshift."
    setup = {
        "label": "B1 V-Kicks Flat-Orbit QShift",
        "beam": 1,
        "plane": "Y",
        "kickac_path": BASE_DIR + sub_dir + "getkickac.out",
        "kickac_out": BASE_DIR + sub_dir + "getkickac_ampdet.out",
        "tune_x": 0.305,
        "tune_y": 0.315,
        "window_length": 200,
        "tune_cut": 0.0005,
        "fine_window": 100,
        "fine_cut": 0.0001,
        "bbq_plot_out": BASE_DIR + id + "bbq.pdf",
        "ampdet_plot_out": BASE_DIR + id + "ampdet.pdf",
        "bbq_out": BASE_DIR + sub_dir + "bbq_ampdet.out",
        "bbq_plot_show": SHOW_PLOTS,
        "ampdet_plot_show": SHOW_PLOTS,
        "ampdet_plot_xmin": XLIM[0],
        "ampdet_plot_xmax": XLIM[1],
        "ampdet_plot_ymin": YLIM[0],
        "ampdet_plot_ymax": YLIM[1],
    }
    return ampdet.analyse_with_bbq_corrections(**setup)


# Beam 1 #######################################################################


def get_new_plots_b1_y_ip5xing():
    sub_dir = "beam1/B1_flatorbit_IP5xing_V/"
    id = "plot.2018.b1.vkicks.ip5xing."
    setup = {
        "label": "B1 V-Kicks IP5 X'ing",
        "beam": 1,
        "plane": "Y",
        "kickac_path": BASE_DIR + sub_dir + "getkickac.out",
        "kickac_out": BASE_DIR + sub_dir + "getkickac_ampdet.out",
        "tune_x": 0.31,
        "tune_y": 0.32,
        "window_length": 200,
        "tune_cut": 0.0005,
        "fine_window": 100,
        "fine_cut": 0.0001,
        "bbq_plot_out": BASE_DIR + id + "bbq.pdf",
        "ampdet_plot_out": BASE_DIR + id + "ampdet.pdf",
        "bbq_out": BASE_DIR + sub_dir + "bbq_ampdet.out",
        "bbq_plot_show": SHOW_PLOTS,
        "ampdet_plot_show": SHOW_PLOTS,
        "ampdet_plot_xmin": XLIM[0],
        "ampdet_plot_xmax": XLIM[1],
        "ampdet_plot_ymin": YLIM[0],
        "ampdet_plot_ymax": YLIM[1],
    }
    return ampdet.analyse_with_bbq_corrections(**setup)


def get_new_plots_b1_y_flat():
    sub_dir = "beam1/B1_flatorbit_V/"
    id = "plot.2018.b1.vkicks.flat."
    setup = {
        "label": "B1 V-Kicks Flat-Orbit",
        "beam": 1,
        "plane": "Y",
        "kickac_path": BASE_DIR + sub_dir + "getkickac.out",
        "kickac_out": BASE_DIR + sub_dir + "getkickac_ampdet.out",
        "tune_x": 0.31,
        "tune_y": 0.32,
        "window_length": 200,
        "tune_cut": 0.002,
        "fine_window": 100,
        "fine_cut": 0.0001,
        "bbq_plot_out": BASE_DIR + id + "bbq.pdf",
        "ampdet_plot_out": BASE_DIR + id + "ampdet.pdf",
        "bbq_out": BASE_DIR + sub_dir + "bbq_ampdet.out",
        "bbq_plot_show": SHOW_PLOTS,
        "ampdet_plot_show": SHOW_PLOTS,
        "ampdet_plot_xmin": XLIM[0],
        "ampdet_plot_xmax": XLIM[1],
        "ampdet_plot_ymin": YLIM[0],
        "ampdet_plot_ymax": YLIM[1],
    }
    return ampdet.analyse_with_bbq_corrections(**setup)


def get_new_plots_b1_x_flat():
    sub_dir = "beam1/B1_flatorbit_H/"
    id = "plot.2018.b1.hkicks.flat."
    setup = {
        "label": "B1 H-Kicks Flat-Orbit",
        "beam": 1,
        "plane": "X",
        "kickac_path": BASE_DIR + sub_dir + "getkickac.out",
        "kickac_out": BASE_DIR + sub_dir + "getkickac_ampdet.out",
        "tune_x": 0.31,
        "tune_y": 0.32,
        "window_length": 200,
        "tune_cut": 0.002,
        "fine_window": 100,
        "fine_cut": 0.0001,
        "bbq_plot_out": BASE_DIR + id + "bbq.pdf",
        "ampdet_plot_out": BASE_DIR + id + "ampdet.pdf",
        "bbq_out": BASE_DIR + sub_dir + "bbq_ampdet.out",
        "bbq_plot_show": SHOW_PLOTS,
        "ampdet_plot_show": SHOW_PLOTS,
        "ampdet_plot_xmin": XLIM[0],
        "ampdet_plot_xmax": XLIM[1],
        "ampdet_plot_ymin": YLIM[0],
        "ampdet_plot_ymax": YLIM[1],
    }
    return ampdet.analyse_with_bbq_corrections(**setup)


def get_new_plots_b1_x_ip5xing():
    sub_dir = "beam1/B1_flatorbit_IP5xing_H/"
    id = "plot.2018.b1.hkicks.ip5xing."
    setup = {
        "label": "B1 H-Kicks IP5 X'ing",
        "beam": 1,
        "plane": "X",
        "kickac_path": BASE_DIR + sub_dir + "getkickac.out",
        "kickac_out": BASE_DIR + sub_dir + "getkickac_ampdet.out",
        "tune_x": 0.31,
        "tune_y": 0.32,
        "window_length": 1000,
        "tune_cut": 0.0007,
        "fine_window": 100,
        "fine_cut": 0.0002,
        "bbq_plot_out": BASE_DIR + id + "bbq.pdf",
        "ampdet_plot_out": BASE_DIR + id + "ampdet.pdf",
        "bbq_plot_show": SHOW_PLOTS,
        "ampdet_plot_show": SHOW_PLOTS,
        "ampdet_plot_xmin": XLIM[0],
        "ampdet_plot_xmax": XLIM[1],
        "ampdet_plot_ymin": YLIM[0],
        "ampdet_plot_ymax": YLIM[1],
    }
    return ampdet.analyse_with_bbq_corrections(**setup)


# Beam 1 Commissioning ########################################################


def get_commish_plots_b1_x():
    sub_dir = "2018_commissioning/"
    id = "plot.2018.b1.hkicks.fullxing."
    setup = {
        "label": "B1 H-Kicks Full X'ing",
        "beam": 1,
        "plane": "X",
        "kickac_path": BASE_DIR + sub_dir + "B1_crossing_H_amp_det.dat_clean",
        "kickac_out": BASE_DIR + sub_dir + "getkickac_ampdet.out",
        "tune_x": 0.31,
        "tune_y": 0.32,
        # "window_length": 100,
        # "tune_cut": 0.005,
        "window_length": 200,
        "tune_cut": 0.0005,
        "fine_window": 100,
        "fine_cut": 0.0001,
        "bbq_plot_out": BASE_DIR + id + "bbq.pdf",
        "ampdet_plot_out": BASE_DIR + id + "ampdet.pdf",
        "bbq_plot_show": SHOW_PLOTS,
        # "bbq_plot_two": True,
        "ampdet_plot_show": SHOW_PLOTS,
        "ampdet_plot_xmin": XLIM[0],
        "ampdet_plot_xmax": XLIM[1],
        "ampdet_plot_ymin": YLIM[0],
        "ampdet_plot_ymax": YLIM[1],
    }
    return ampdet.analyse_with_bbq_corrections(**setup)


if __name__ == '__main__':
    figs_com = get_commish_plots_b1_x()
    # figs_new = get_new_plots_b1_x_flat()
    # figs_new = get_new_plots_b1_x_ip5xing()
    # figs_new = get_new_plots_b1_y_flat()
    # figs_new = get_new_plots_b1_y_ip5xing()
    # figs_new = get_new_plots_b1_y_flat_qshift()
    # figs_new = get_new_plots_b1_y_ip5xing_qshift()
    # figs_new = get_new_plots_b2_x_flat()
    # figs_new = get_new_plots_b2_x_ip5xing()
    # figs_new = get_new_plots_b2_y_flat()
    # figs_new = get_new_plots_b2_y_ip5xing()
    plt.show()
