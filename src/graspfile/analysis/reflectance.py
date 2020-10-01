import numpy as np


def reflectance(n1, n2):
    """Calculate the amplitude reflection coefficient due to moving from media with index n1 to media with index n2.

    Args:
        n1 (float:): Refractive index of media 1.
        n2 (float:): Refractive index of media 2.

    Returns:
        float: Reflection coefficient"""
    return (n1 - n2) / (n1 + n2)


def transmittance(n1, n2):
    """Calculate the amplitude transmission coefficient due to moving from media with index n1 to media with index n2.

    Args:
        n1 (float:): Refractive index of media 1.
        n2 (float:): Refractive index of media 2.

    Returns:
        float: Transmission coefficient"""
    return np.sqrt(1.0 - ((n1 - n2) / (n1 + n2)) ** 2)


def total_transmittance(ns):
    """Calculate the total transmission coeffficient due to moving through media with listed indices.  No interference
    is included, making this calculation suitable for cascaded PO calculations in GRASP.

    Args:
        ns (list: of float:): List of refractive indices of media

    Returns:
        float: total transmittance."""
    t = 1.0
    for i in range(len(ns) - 1):
        t *= transmittance(ns[i], ns[i + 1])

    return t
