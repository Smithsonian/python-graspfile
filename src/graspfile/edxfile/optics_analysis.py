import numpy as np
import numpy.ma as ma

# Get arrays of x and y values in field
def getXYvals(field):
    x_vals = np.linspace(field.gridMin_x, field.gridMax_x, field.gridN_x)
    y_vals = np.linspace(field.gridMin_y, field.gridMax_y, field.gridN_y)
    return x_vals, y_vals

def getXYmesh(field):
    x_vals, y_vals = getXYvals(field)
    xv, yv = np.meshgrid(x_vals, y_vals)
    return xv, yv


def findPeak(field, comp=0, maxRadius=None, minRadius=None):
    """Find the peak magnitude of component comp in the field

    Search can be limited to maximum Radius from center."""
    x_vals, y_vals = getXYvals(field)
    xv, yv = getXYmesh(field)

    f = abs(field.field[:,:,comp])
    if maxRadius != None:
        rad = xv**2 + yv**2
        radM = ma.masked_greater(rad, maxRadius**2)
        f = ma.array(f, mask=radM.mask)

    if minRadius != None:
        rad = xv**2 + yv**2
        radm = ma.masked_less(rad, minRadius**2)
        f = ma.array(f, mask=radm.mask)

    ny, nx = np.unravel_index(np.argmax(abs(f)), f.shape)
    xPeak = x_vals[nx]
    yPeak = y_vals[ny]

    return xPeak, yPeak

# find the center of illumination of the field
def findIllumCenter(field, comp=0, trunc_level=0.0, maxRadius=None, minRadius=None):
    """Find the center of illumination by finding the "center of mass" of the field"""
    xv, yv = getXYmesh(field)

    f = abs(field.field[:,:,comp])
    if trunc_level != 0.0:
        f = ma.masked_less_equal(f, trunc_level)
        xv = ma.array(xv, mask=f.mask)
        yv = ma.array(yv, mask=f.mask)

    if maxRadius != None:
        rad = xv**2 + yv**2
        radM = ma.masked_greater(rad, maxRadius**2)
        f = ma.array(f, mask=radM.mask)
        xv = ma.array(xv, mask=radM.mask)
        yv = ma.array(yv, mask=radM.mask)

    if minRadius != None:
        radm = ma.masked_less(rad, minRadius**2)
        f = ma.array(f, mask=radm.mask)
        xv = ma.array(xv, mask=radm.mask)
        yv = ma.array(yv, mask=radm.mask)

    xIllum = xv*f
    yIllum = yv*f

    norm = np.sum(f)

    xCent = np.sum(xIllum)/norm
    yCent = np.sum(yIllum)/norm

    return xCent, yCent
