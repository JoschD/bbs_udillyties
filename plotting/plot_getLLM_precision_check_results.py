"""
Plots output and comparative output for analysed data. It is assumed, that one or more method
(like sussix or harpy) is run on the data and getLLM then on the resulting data.

The configuration of the used methods and locations will be loaded from a given config-python file
containing a dictonary opt, with the appropriate fields. (standard config.py)

The method results are supposed to be in subfolders of the same parent folder (opt['dir']['src'])
and are named

opt['prefix']['results']%method%

Inside these folders there should be the getllm subfolders, named

opt['prefix']['getllm']%method%

"""
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import importlib


def _add_repository_to_path():
    # only works if you are already inside the Beta_Beat repository
    directory = os.path.dirname(__file__)
    while 'doc' not in os.listdir(os.path.abspath(directory)):
        directory = os.path.join(directory, '..')
    sys.path.append(os.path.abspath(directory))

_add_repository_to_path()
from tfs_files import tfs_pandas as tfs
from plotshop import plot_style as ps

# take special care when subtracting phases
phase_param_contains = ['phase', 'mu']


# columns in twiss files
column_map = {
    'tunex': 'TUNEX',
    'tuney': 'TUNEY',
    'dtunex': 'TUNEX',
    'dtuney': 'TUNEY',
    'nattunex': 'NATTUNEX',
    'nattuney': 'NATTUNEY',
    'dnattunex': 'NATTUNEX',
    'dnattuney': 'NATTUNEY',
    'betax': 'BETX',
    'betay': 'BETY',
    'betaxmdl': 'BETXMDL',
    'betaymdl': 'BETYMDL',
    'ampbetax': 'BETX',
    'ampbetay': 'BETY',
    'ampbetaxmdl': 'BETXMDL',
    'ampbetaymdl': 'BETYMDL',
    'phasex': 'PHASEX',
    'phasey': 'PHASEY',
    'phasexmdl': 'PHXMDL',
    'phaseymdl': 'PHYMDL',
    'phasetotx': 'PHASEX',
    'phasetoty': 'PHASEY',
    'phasetotxmdl': 'PHXMDL',
    'phasetotymdl': 'PHYMDL',
    '1001R': 'F1001R',
    '1001I': 'F1001I',
    '1010R': 'F1010R',
    '1010I': 'F1010I',
}


# titles to use
title_map = {
    'tunex': 'Tune X',
    'tuney': 'Tune Y',
    'dtunex': 'Tune Difference X',
    'dtuney': 'Tune Difference Y',
    'nattunex': 'Natural Tune X',
    'nattuney': 'Natural Tune Y',
    'dnattunex': 'Natural Tune Diff X',
    'dnattuney': 'Natural Tune Diff Y',
    'betax': 'Beta X',
    'betay': 'Beta Y',
    'ampbetax': 'Beta X from Amp',
    'ampbetay': 'Beta Y from Amp',
    'phasex': 'Phase X',
    'phasey': 'Phase Y',
    'phasetotx': 'Total Phase X',
    'phasetoty': 'Total Phase Y',
    '1001R': 'Coupling $f_{1001}$ Real',
    '1001I': 'Coupling $f_{1001}$ Imag',
    '1001': 'Coupling $f_{1001}$ Amp',
    '1010R': 'Coupling $f_{1010}$ Real',
    '1010I': 'Coupling $f_{1010}$ Imag',
    '1010': 'Coupling $f_{1010}$ Amp',
    'harpy_svd': 'HARPY-SVD',
    'harpy_fast': 'HARPY-FAST',
    'harpy_bpm': 'HARPY-BPM',
    'sussix': 'SUSSIX',
    'model': 'Model',
}


"""
======================== Main plotting Functions ========================
"""


def plot_getllm_comparison(opt):
    _check_opt(opt)
    _create_output_folders(opt)
    _plot_data(opt)


def _plot_data(opt):
    ps.set_style(opt['plot']['style'], manual=opt['plot']['manual_style'])
    _plot_beta(opt)
    _plot_param('phase', opt)
    _plot_param('phasetot', opt)
    _plot_tune(opt)
    _plot_coupling(opt)


def _plot_param(param, opt):
    methods = _get_methods(opt)

    for plane in ['x', 'y']:
        fig, ax = _initialize_plot()

        full_param = param + plane
        col_name = column_map[full_param]
        title = _get_title(full_param, opt)
        if _cmp_to_method(opt):
            data_sub = _get_param_data(full_param, opt['analysis']['compare_to'], opt)

        for method in methods:
                data = _get_param_data(full_param, method, opt)
                data_out = _empty_tfs_from(data)
                if _cmp_to_model(opt):
                    col_mdl_name = column_map[full_param + 'mdl']
                    data_out[col_name] = \
                        _sub_tfs(data[col_name], data[col_mdl_name], axis=0, param=param)
                elif _cmp_to_method(opt):
                    data_out[col_name] = \
                        _sub_tfs(data[col_name], data_sub[col_name], axis=0, param=param)
                else:
                    data_out[col_name] = data[col_name]
                plt.plot(data_out['S'], data_out[col_name], label=method)

        _finalize_plot(fig, ax, param, title, plane, opt)


def _plot_beta(opt):
    methods = _get_methods(opt)

    for beta in ['beta', 'ampbeta']:
        for plane in ['x', 'y']:
            fig, ax = _initialize_plot()

            beta_str = beta + plane
            col_name = column_map[beta_str]
            title = _get_beta_title(beta_str, opt)
            if _cmp_to_method(opt):
                beta_sub = _get_beta_beating(beta_str, opt['analysis']['compare_to'], opt)

            for method in methods:
                    if _cmp_to_model(opt):
                        beta_df = _get_beta_beating(beta_str, method, opt)
                    elif _cmp_to_method(opt):
                        beta_df = _get_beta_beating(beta_str, method, opt)
                        beta_df[col_name] = beta_df[col_name].sub(
                            beta_sub[col_name], axis=0)
                    else:
                        beta_df = _get_param_data(beta_str, method, opt)
                    plt.plot(beta_df['S'], beta_df[col_name], label=method)

            if _cmp_to_model(opt) or _cmp_to_method(opt):
                _finalize_plot(fig, ax, 'betabeat', title, plane, opt)
            else:
                _finalize_plot(fig, ax, 'beta', title, plane, opt)


def _plot_tune(opt):
    methods = _get_methods(opt)
    if _cmp_to_model(opt):
        model_tunes = _get_model_tunes(opt)

    for plane in ['x', 'y']:
        if _cmp_to_method(opt):
            data_sub = _get_harmonic_data(opt['analysis']['compare_to'], plane, opt)

        tune_str = 'tune' + plane
        nat_str = 'nattune' + plane

        fig, ax = _initialize_plot()
        fig_nat, ax_nat = _initialize_plot()

        title = _get_title(tune_str, opt)
        title_nat = _get_title(nat_str, opt)

        for method in methods:
                data = _get_harmonic_data(method, plane, opt)
                data_out = _empty_tfs_from(data)

                if _cmp_to_model(opt):
                    data_out[tune_str] = \
                        data[column_map[tune_str]] - model_tunes[tune_str]
                    data_out[nat_str] = \
                        data[column_map[nat_str]] - model_tunes[nat_str]
                elif _cmp_to_method(opt):
                    data_out[tune_str] = \
                        data[column_map[tune_str]] - data_sub[column_map[tune_str]]
                    data_out[nat_str] = \
                        data[column_map[nat_str]] - data_sub[column_map[nat_str]]
                else:
                    data_out[tune_str] = data[column_map[tune_str]]
                    data_out[nat_str] = data[column_map[nat_str]]

                ax.plot(data['S'], data_out[tune_str], label=method)
                ax_nat.plot(data['S'], data_out[nat_str], label=method)

        _finalize_plot(fig, ax, 'tune', title, plane, opt)
        _finalize_plot(fig_nat, ax_nat, 'nattune', title_nat, plane, opt)


def _plot_coupling(opt):
    methods = _get_methods(opt)
    if _cmp_to_method(opt):
        data_sub = _get_param_data('couple', opt['analysis']['compare_to'], opt)

    for plane in ['1001', '1010']:
        for ext in ['R', 'I', '']:
            couple = plane + ext

            if couple == plane:
                col_name = couple
                col_r = column_map[couple + 'R']
                col_i = column_map[couple + 'I']
            else:
                col_name = column_map[couple]

            fig, ax = _initialize_plot()
            title = _get_coupling_title(couple, opt)

            for method in methods:
                    data = _get_param_data('couple', method, opt)
                    data_diff = _empty_tfs_from(data)
                    if couple == plane:
                        if _cmp_to_method(opt):
                            data_diff[col_name] = _abs_tfs(data, col_r, col_i).sub(
                                _abs_tfs(data_sub, col_r, col_i), axis=0)
                        else:
                            data_diff[col_name] = _abs_tfs(data, col_r, col_i)
                    else:
                        if _cmp_to_method(opt):
                            data_diff[col_name] = data[col_name].sub(data_sub[col_name])
                        else:
                            data_diff[col_name] = data[col_name]

                    plt.plot(data_diff['S'], data_diff[col_name], label=method)
            _finalize_plot(fig, ax, 'couple'+ext, title, plane, opt)


"""
======================== plotting Helper Functions ========================
"""


def _initialize_plot():
    fig, ax = plt.subplots()
    plt.sca(ax)
    return fig, ax


def _finalize_plot(fig, ax, param, title, plane, opt):
    ax.set_title(title)
    if opt['plot']['legend']:
        ymove = fig.get_figwidth() / 150  # empirical...
        ax.legend(loc='upper right', frameon=True, bbox_to_anchor=[1 + ymove, 1])
        ax.set_position(ax.get_position().translated(-ymove/5, 0))
    ax.set_xlabel(ax.get_xlabel(), labelpad=4)
    ax.set_ylabel(ax.get_ylabel(), labelpad=5)
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 3))

    ps.set_xaxis_label(ax)
    ps.set_yaxis_label(ax, plane, param)
    ps.set_xLimits('LHCB1', ax)
    ps.show_ir(_get_ip_positions(opt), ax)

    _save_figure(fig,
                 title.replace(" ", "_").replace("$", "").replace("{", "").replace("}", ""),
                 opt)
    plt.close(fig)


def _save_figure(fig, name, opt):
    """
    Saves the figure to files specified by their extension in opt['plot']['ext']
    :param fig: Figure to export
    :param name: Name of the output file
    :param opt: opt-structure
    :return: Nothing
    """
    plt.draw()
    for ext in opt['plot']['ext']:
        out_path = os.path.join(opt['dir']['plots'], name + '.' + ext)
        fig.savefig(out_path, format=ext, dpi=800)


def _get_beta_title(param, opt):
    title = title_map[param]
    if _cmp_to_model(opt):
        title += ' Beating'
    elif _cmp_to_method(opt):
        title += ' Beatig diff to ' + title_map[opt['analysis']['compare_to']]
    return title


def _get_coupling_title(param, opt):
    title = title_map[param]
    if _cmp_to_method(opt):
        title += ' diff to ' + title_map[opt['analysis']['compare_to']]
    return title


def _get_title(param, opt):
    title = title_map[param]
    if _cmp_to_model(opt) or _cmp_to_method(opt):
        title += ' diff to ' + title_map[opt['analysis']['compare_to']]
    return title


"""
======================== Option Handling ========================
"""


def get_opt_from_cfg(cfg_path='config'):
    """
    Dynamically imports the config file and returns it
    """
    try:
        opt = importlib.import_module(cfg_path).opt
    except ImportError:
        raise IOError("Could not load config file: '" + cfg_path + "'")
    return opt


def _check_opt(opt):
    """
    Adds the Beta-Beat Repository to the path and imports tfs_pandas.
    TODO: opt-fields should be checked if correct
    """
    # TODO: check opt for appropriate fields, raise OptionError
    pass


def _cmp_to_model(opt):
    return opt['analysis']['compare_to'] == 'model'


def _cmp_to_method(opt):
    return not _cmp_to_model(opt) and not opt['analysis']['compare_to'] == ''


def _get_methods(opt):
    methods = list(opt['analysis']['methods'])
    if _cmp_to_method(opt):
        try:
            methods.pop(methods.index(opt['analysis']['compare_to']))
        except ValueError:
            pass
    return methods

"""
======================== Paths ========================
"""


def _get_method_fullpath(method, opt):
    return os.path.join(opt['dir']['src'],
                        opt['prefix']['results'] + method)


def _get_getllm_fullpath(method, opt):
    return os.path.join(_get_method_fullpath(method, opt),
                        opt['prefix']['getllm'] + method)


def _get_twiss_kicker_path(opt):
    """
    Returns the full filepath to the kicker model, if present. Otherwise None
    """
    acd_path = _get_twiss_acd_path(opt)
    adt_path = _get_twiss_adt_path(opt)
    if os.path.exists(acd_path):
        return acd_path
    elif os.path.exists(adt_path):
        return adt_path
    else:
        return None


def _get_ip_positions(opt):
    df = tfs.read_tfs(_get_twiss_elements_path(opt)).set_index('NAME')
    ip_names = ["IP" + str(i) for i in range(1, 9)]
    ip_pos = df.loc[ip_names, 'S'].values
    return dict(zip(ip_names, ip_pos))


def _get_twiss_path(opt):
    return os.path.join(opt['dir']['model'], "twiss.dat")


def _get_twiss_acd_path(opt):
    return os.path.join(opt['dir']['model'], "twiss_ac.dat")


def _get_twiss_adt_path(opt):
    return os.path.join(opt['dir']['model'], "twiss_adt.dat")


def _get_twiss_elements_path(opt):
    return os.path.join(opt['dir']['model'], "twiss_elements.dat")


def _get_tbt_path(method, opt):
    return os.path.join(_get_method_fullpath(method, opt), opt['filename'])


def _get_harmonic_path(method, plane, opt):
    harmonic_path = os.path.join(_get_method_fullpath(method, opt),
                                 opt['filename'] + ".lin" + plane)
    if not os.path.exists(harmonic_path):
        harmonic_path = os.path.join(_get_method_fullpath(method, opt),
                                     opt['filename'] + "_lin" + plane)
    return harmonic_path


def _create_output_folders(opt):
    if not os.path.exists(opt['dir']['plots']):
        os.mkdir(opt['dir']['plots'])


"""
======================== Data Handling ========================
"""


def _get_param_data(param, method, opt):
    """
    Get all getLLM data as DataFrame from subfolder in method and parameter param
    """
    directory = _get_getllm_fullpath(method, opt)
    df = tfs.read_tfs(os.path.join(directory, 'get' + param + '_free.out'))
    df.set_index('NAME', inplace=True)
    return df


def _get_harmonic_data(method, plane, opt):
    file_path = _get_harmonic_path(method, plane, opt)
    df = tfs.read_tfs(file_path)
    df.set_index('NAME', inplace=True)
    return df


def _get_model_tunes(opt):
    twiss_kick_path = _get_twiss_kicker_path(opt)
    if not twiss_kick_path:
        raise IOError("Tune Model not found. Hint: Works only with adt or acd kicks!")
    df_kick = tfs.read_tfs(twiss_kick_path)
    df = tfs.read_tfs(_get_twiss_path(opt))
    data = {
        'tunex': df_kick.headers['Q1'] % 1,
        'tuney': df_kick.headers['Q2'] % 1,
        'nattunex': df.headers['Q1'] % 1,
        'nattuney': df.headers['Q2'] % 1,
    }
    return data


def _get_beta_beating(beta_str, method, opt):
    """
    Calculate Beta-Beating from Data in file.
    """
    data = _get_param_data(beta_str, method, opt)
    beta_beat = tfs.TfsDataFrame(index=data.index)
    beta_beat[column_map[beta_str]] = data[column_map[beta_str]].sub(
        data[column_map[beta_str + 'mdl']], axis=0
    ).div(
        data[column_map[beta_str + 'mdl']], axis=0
    )
    beta_beat = beta_beat.join(data['S'])
    return beta_beat


def _empty_tfs_from(tfs_in):
    """
    Create an empty Dataframe containing the index and the 'S'-position values of
    tfs_in but nothing else

    :param tfs_in: Dataframe with an 'S' column
    :return: New Dataframe
    """
    data_diff = tfs.TfsDataFrame(index=tfs_in.index)
    data_diff = data_diff.join(tfs_in['S'])
    return data_diff


def _abs_tfs(data, col_r, col_i):
    """
    Calculates the absulute value from two columns containing
    the real and imaginary part respectively

    :param data: Dataframe containing real and imag columns
    :param col_r: Columnname for real part
    :param col_i: Columnname for imaginary part
    :return: Series of absolute values from real and imag colums
    """
    return (data[col_r]**2 + data[col_i]**2)**.5


def _sub_tfs(tfs_min, tfs_sub, axis, param):
    """
    Subtract two pandas dataframes/series while taking care of phase-wrapping

    :param tfs_min: Dataframe/Series to subtract from (minuend)
    :param tfs_sub: Dataframe/Series to subtract (subtrahend)
    :param axis: Along this axis
    :param param: The parameter, that is currently investigated
    (only to check if its a phase param, does NOT choose columns!)
    :return : difference (modified tfs_min)
    """
    if any([phs in param for phs in phase_param_contains]):
        return (tfs_min.sub(tfs_sub, axis=axis) + .5) % 1 - .5
    else:
        return tfs_min.sub(tfs_sub, axis=axis)


def _phs_to_cplx(x):
    return np.exp(-2j*np.pi*x)


def _cplx_to_phs(x):
    return np.angle(x) / (-2*np.pi)

"""
======================== Main ========================
"""

if __name__ == "__main__":
    _opt = get_opt_from_cfg('plot_getLLM_precision_check_results_cfg')
    plot_getllm_comparison(_opt)
