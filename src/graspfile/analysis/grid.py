import numpy as np
import numpy.ma as ma


def find_peak(field, comp=0, max_radius=None, min_radius=None):
    """Find the peak magnitude of a component in the field.

    Args:
        field ``GraspField``: The field to work on.
        comp int: The field component to look at.
        max_radius float: Ignore portions of the grid outside this radius from the center of the field.
        min_radius float: Ignore portions of the grid inside this radius from the center fo the field.

    Returns:
        x_peak float:, y_peak float: The x and y values of the peak value."""
    x_vals, y_vals = field.positions_1d

    f = abs(field.field[:, :, comp])
    if max_radius is not None:
        rad = field.radius_grid()
        rad_max_mask = ma.masked_greater(rad, max_radius)
        f = ma.array(f, mask=rad_max_mask.mask)

    if min_radius is not None:
        rad = field.radius_grid()
        rad_min_mask = ma.masked_less(rad, min_radius)
        f = ma.array(f, mask=rad_min_mask.mask)

    ny, nx = np.unravel_index(np.argmax(abs(f)), f.shape)
    x_peak = x_vals[nx]
    y_peak = y_vals[ny]

    return x_peak, y_peak


# find the center of illumination of the field
def find_center(field, comp=0, trunc_level=0.0, max_radius=None, min_radius=None):
    """Find the center of illumination by finding the "center of mass" of the field.

    Parameters:
        field ``GraspField``: The field to work on.
        comp int: The field component to look at.
        trunc_level float: Ignore the contributions from portions of the grid below this field level.
        max_radius float: Ignore portions of the grid outside this radius from the center of the field.
        min_radius float: Ignore portions of the grid inside this radius from the center fo the field.

    Returns:
        x_cent float, y_cent float: The x and y values of the center of the field."""
    xv, yv = field.positions

    f = abs(field.field[:, :, comp])
    if trunc_level != 0.0:
        f = ma.masked_less_equal(f, trunc_level)
        xv = ma.array(xv, mask=f.mask)
        yv = ma.array(yv, mask=f.mask)

    if max_radius is not None:
        rad = field.radius_grid()
        rad_max_mask = ma.masked_greater(rad, max_radius)
        f = ma.array(f, mask=rad_max_mask.mask)
        xv = ma.array(xv, mask=rad_max_mask.mask)
        yv = ma.array(yv, mask=rad_max_mask.mask)

    if min_radius is not None:
        rad = field.radius_grid()
        rad_min_mask = ma.masked_less(rad, min_radius)
        f = ma.array(f, mask=rad_min_mask.mask)
        xv = ma.array(xv, mask=rad_min_mask.mask)
        yv = ma.array(yv, mask=rad_min_mask.mask)

    x_illum = xv * f
    y_illum = yv * f

    norm = np.sum(f)

    x_cent = np.sum(x_illum) / norm
    y_cent = np.sum(y_illum) / norm

    return x_cent, y_cent


def combine_grids(grids, coherent=True):
    """Sum fields from different grid files.

    Assumes that all fields across grids have the same positions, size, etc.

    Args:
        grids list: of ``GraspGrid``: List of grid objects to combine.
        coherent bool: Determines whether to form coherent or incoherent sum. Defaults to coherent as that is the more
                        likely use case.
    Returns:
        ``GraspGrid``: A grid object containing a field for each of the matched fields in the supplied list of grids."""
    new_grid = np.copy.deepcopy(grids[0])
    for n, field in enumerate(new_grid.fields):
        new_grid.fields[n].field = np.zeros_like(grids[0].fields[n].field)
        for g, grid in enumerate(grids):
            if coherent:
                new_grid.fields[n].field += grids[g].fields[n].field
            else:
                new_grid.fields[n].field += np.abs(grids[g].fields[n].field)
