import numpy as np


def norm_0_1(array):
    """Return array normalized to values between 0 and 1"""
    return (array - np.min(array)) / (np.max(array - np.min(array)))
