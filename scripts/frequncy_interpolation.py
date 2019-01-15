from __future__ import division
import numpy as np

PI2I = 2 * np.pi * complex(0, 1)


def laskar_method(tbt, num_harmonics):
    samples = tbt[:]  # Copy the samples array.
    n = len(samples)
    int_range = np.arange(n)
    coefficients = []
    frequencies = []
    for _ in range(num_harmonics):
        # Compute this harmonic frequency and coefficient.
        frequency = _jacobsen(np.fft.fft(samples), n)
        coefficient = _compute_coef(samples, frequency)
        # Store frequency and coefficient
        coefficients.append(coefficient)
        frequencies.append(frequency)
        # Subtract the found pure tune from the signal
        new_signal = coefficient * np.exp(PI2I * frequency * int_range)
        samples = samples - new_signal
    coefficients, frequencies = zip(*sorted(zip(coefficients, frequencies),
                                            key=lambda tuple: np.abs(tuple[0]), reverse=True))
    return frequencies, coefficients


def _jacobsen(dft_values, n):
    """
    This method interpolates the real frequency of the
    signal using the three highest peaks in the FFT.
    """
    k = np.argmax(np.abs(dft_values))
    r = dft_values
    delta = np.tan(np.pi / n) / (np.pi / n)
    kp = (k + 1) % n
    km = (k - 1) % n
    delta = delta * np.real((r[km] - r[kp]) / (2 * r[k] - r[km] - r[kp]))
    return (k + delta) / n


def _compute_coef(samples, freq):
    """
    Computes the coefficient of the Discrete Time Fourier
    Transform corresponding to the given frequency.
    """
    n = len(samples)
    exponents = np.exp(-PI2I * freq * np.arange(n))
    coef = np.sum(exponents * samples) / n
    return coef

if __name__ == '__main__':
    i = 2 * np.pi * np.arange(4096)
    data = np.cos(0.134 * i) + np.cos(0.244 * i) + 0.01 * np.random.randn(4096)
    freqs, coeffs = laskar_method(data, 300)
