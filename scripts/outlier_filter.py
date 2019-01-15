""" Filter outliers of normally distributed data by sigmas."""

from __future__ import division
import numpy as np
from scipy.stats import t
import matplotlib.pyplot as plt


def get_filter_mask(data, x_data=None, limit=0.0, niter=20):
    """
    It filters the array of values which are meant to be constant
    or a linear function of the other array if that is provided
    Returns a filter mask for the original array
    Assumes the values are normally distributed, i.e. uses t-student distribution
    """
    mask = np.ones(len(data), dtype=bool)
    nsigmas = t.ppf([1 - 0.5 / len(data)], len(data))
    prevlen = np.sum(mask) + 1
    for _ in range(niter):
        if not ((np.sum(mask) < prevlen) and (np.sum(mask) > 2)):
            break
        prevlen = np.sum(mask)
        if x_data is not None:
            m, b = np.polyfit(x_data[mask], data[mask], 1)
            y, y_orig = data[mask] - b - m * x_data[mask], data - b - m * x_data
        else:
            y, y_orig = data[mask], data[:]
        mask = np.abs(y_orig - np.mean(y)) < np.max([limit, nsigmas * np.std(y)])
    return mask


if __name__ == '__main__':
    x_data = 100 * np.random.rand(1000)
    y_data = 0.35 * x_data + np.random.randn(1000)
    y_data[-100:] = y_data[99::-1]
    x_data[:50] = 38 + np.random.randn(50)
    mask = get_filter_mask(y_data, x_data=x_data)
    f, ax = plt.subplots(1)
    ax.plot(x_data, y_data, 'ro')
    ax.plot(x_data[mask], y_data[mask], 'bo')
    plt.show()
