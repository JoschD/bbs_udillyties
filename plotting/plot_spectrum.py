import matplotlib.pyplot as plt
import matplotlib.collections as mc
import numpy as np
from numpy import fft
import pandas as pd
import plotshop.plot_style as ps


PI2I = np.pi*2j


class ArgumentError(Exception):
    pass


"""
======================== Helper Functions ========================
"""


def _get_dft_spectrum(names, matrix):
    print "-> Getting Spectrum"
    frequencies = np.broadcast_to(fft.fftfreq(matrix.shape[1]), matrix.shape)
    coefficients = fft.fft(matrix, axis=1)

    coefs = pd.DataFrame(data=coefficients, index=names)
    freqs = pd.DataFrame(data=frequencies, index=names)
    return {"COEFS": coefs, "FREQS": freqs}


def _get_center(harpy_input, tune):
    tune = tune.lower()
    if tune == 'tunex':
        center = harpy_input.tunex
    elif tune == 'tuney':
        center = harpy_input.tuney
    elif tune == 'nattunex':
        center = harpy_input.nattunex
    elif tune == 'nattuney':
        center = harpy_input.nattuney
    else:
        raise ArgumentError("Tune '" + tune + "' unknown")
    return center


def _compute_coef_simple(samples, kprime):
    """
    Computes the coefficient of the Discrete Time Fourier
    Transform corresponding to the given frequency (kprime).
    """
    n = len(samples)
    freq = kprime / n
    exponents = np.exp(-PI2I * freq * np.arange(n))
    coef = np.sum(exponents * samples)
    return coef


def _add_tunes_to_ax(ax, harpy_input, plane):
    """
    Add tune and nattune lines to given axes.
    Y-Limits of ax should have been set before.
    """

    tune = _get_center(harpy_input, 'tune' + plane)
    nattune = _get_center(harpy_input, 'nattune' + plane)
    ylim = ax.get_ylim()
    ypos = ylim[0] + (ylim[1] - ylim[0]) * 1.05
    ax.text(tune, ypos, 'Tune', color='grey', ha='center')
    ax.axvline(tune, linestyle=':', color='grey')
    ax.text(nattune, ypos, 'Nattune', color='grey', ha='center')
    ax.axvline(nattune, linestyle=':', color='grey')


def _get_sorted_amp_and_freq(spectrum):
    print "-> plotting Spectrum"
    dec_places = 7

    print "  |- Get Frequencies and Amplitudes"
    freqs = spectrum['FREQS'].round(dec_places).values.ravel()
    amps = spectrum['COEFS'].apply(np.abs)
    amps = 10 * amps.div(amps.max(axis=1), axis=0).apply(np.log10)
    amps = amps.values.ravel()
    amp_range = [np.min(amps), 0]

    print "  |- Sorting amplitudes by frequencies"
    f_unique = np.unique(freqs)

    amps_by_freqs = [[] for _ in range(len(f_unique))]
    for f, a in zip(freqs, amps):
        amps_by_freqs[np.where(f_unique == f)[0][0]] += [a]  # I am sorry..

    return f_unique, amps_by_freqs, amp_range


"""
======================== plotting Functions ========================
"""


def plot_spectrum3D(spectrum, harpy_input, tune):
    print "-> plotting Spectrum"
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    freqs = spectrum['FREQS'].values
    amps = spectrum['COEFS'].apply(np.abs).values
    center = _get_center(harpy_input, tune)

    xlim = center + np.array([-1, +1]) * 0.01

    color_map = plt.cm.jet(np.linspace(0, 1, freqs.shape[0]))
    for idx_bpm in range(0, freqs.shape[0], 50):
        mask = (xlim[0] <= freqs[idx_bpm, :]) & (freqs[idx_bpm, :] <= xlim[1])

        l = sum(mask)
        y = np.ones(l) * idx_bpm
        z = np.zeros(l)
        dx = np.ones(l) * harpy_input.tolerance / 30
        dy = np.zeros(l)
        ax.bar3d(freqs[idx_bpm, mask], y, z,
                 dx, dy, amps[idx_bpm, mask],
                 color=color_map[idx_bpm]
                 )

    plt.draw()
    plt.show()


def plot_spectrum25D(spectrum, harpy_input, plane):
    nbins = 20

    freqs, amps, amp_range = _get_sorted_amp_and_freq(spectrum)
    df = np.min(freqs[1:] - freqs[:-1])/2

    blocks = []
    values = []
    av = np.empty(len(freqs))
    print "  |- Calculating histograms"
    for i, f in enumerate(freqs):
        # get histogram values
        amp_range_in_f = [np.min(amps[i]), np.max(amps[i])]
        a = np.histogram(amps[i], bins=nbins, range=amp_range_in_f)
        av[i] = np.average(amps[i])

        # define xy-values of blocks (counter clockwise, start=bottom left)
        y = np.append(amp_range[0], a[1])  # add empty bottom block
        yp = np.c_[y[:-1], y[:-1], y[1:], y[1:]]
        xp = np.repeat([[f - df, f + df, f + df, f - df]], nbins + 1, axis=0)

        # add to list of blocks and values
        blocks.append(np.dstack((xp, yp)))
        values.append(np.append(0, a[0]))

    blocks = np.concatenate(blocks, 0)
    values = np.concatenate(values, 0)
    pc = mc.PolyCollection(blocks, cmap='jet', edgecolors=None)
    pc.set_array(values)

    print "  |- Actual plotting"
    ps.set_style('presentation', manual={'lines.marker': '', 'grid.alpha': 0.2})
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlim([freqs[0], freqs[-1]])
    ax.set_ylim(amp_range)
    ax.set_ylabel('Relative Amplitude dB')
    ax.set_xlabel('Frequency Hz')
    ax.set_title('Spectrum of plane ' + plane.upper())

    _add_tunes_to_ax(ax, harpy_input, plane)
    ax.add_collection(pc)

    ax.plot(freqs, av, label='average', color='black', linestyle='--')

    plt.colorbar(mappable=pc)
    plt.draw()
    plt.show()
    pass


def plot_spectrum2D(spectrum, harpy_input, plane):
    freqs, amps, amp_range = _get_sorted_amp_and_freq(spectrum)
    print "  |- Calculating averages"
    for i in range(len(freqs)):
        print "    freq {:d} of {:d}".format(i, len(freqs))
        amps[i] = np.average(amps[i])

    print "  |- Actual plotting"
    ps.set_style('presentation')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlim([freqs[0], freqs[-1]])
    ax.set_ylim(amp_range)
    ax.set_ylabel('Relative Amplitude dB')
    ax.set_xlabel('Frequency Hz')
    ax.set_title('Averaged Spectrum of plane ' + plane.upper())

    ax.plot(freqs, amps, label='average')
    _add_tunes_to_ax(ax, harpy_input, plane)

    plt.draw()
    plt.show()


"""
======================== Main Functions ========================
"""


def plot_dft_spectrum2D(bpm_names, bpm_matrix, harpy_input, plane):
    spectr = _get_dft_spectrum(bpm_names, bpm_matrix)
    plot_spectrum2D(spectr, harpy_input, plane.lower())


def plot_dft_spectrum25D(bpm_names, bpm_matrix, harpy_input, plane):
    spectr = _get_dft_spectrum(bpm_names, bpm_matrix)
    plot_spectrum25D(spectr, harpy_input, plane.lower())
