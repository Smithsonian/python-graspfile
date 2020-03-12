import numpy as np


def find_nearest_idx(array, value):
    """Return the index of nearest value in an array to the given value"""
    idx = (np.abs(array-value)).argmin()
    return idx


def find_nearest(array, value):
    """Return the nearest value in an array to the given value"""
    return array[find_nearest_idx(array, value)]
