"""This is the module for manipulating grid files containing one or more field cuts from TICRA Tools, GRASP and CHAMP
"""


import numpy


class GraspField:
    """Object holding a single dataset from a Grasp field on grid output file (*.grd)

    The field is held in a complex numpy array of shape (grid_n_x, grid_n_y, ncomp)
    where grid_n_x and grid_n_y set the number of points in the grid and ncomp is the
    number of field components"""

    # This layout of array should mean that the polarisation components for a point
    # are contiguous memory, allowing rapid calculation of stokes parameters, etc.

    def __init__(self):
        # initialize storage variables
        # Beam centre in [x,y] form
        self.beam_centre = [0.0, 0.0]

        # Grid parameters
        self.grid_min_x = 0.0
        self.grid_min_y = 0.0
        self.grid_max_x = 0.0
        self.grid_max_y = 0.0
        self.grid_n_x = 0
        self.grid_n_y = 0
        self.grid_step_x = 0.0
        self.grid_step_y = 0.0
        self.k_limit = 0  # Is grid sparse (0=filled, 1=sparse)
        self.ncomp = 0

        # the field object is numpy array of shape (grid_n_x, grid_n_y, ncomp)
        self.field = None

    def read_grasp_field(self, f, ncomp):
        """Reads the Grasp dataset from the file object passed in.  This assumes that
        it is being called from the graspGrid classes read_grasp_grid(f) method, so that
        the file object is already at the start of the record"""

        # find the grid physical extents
        line = f.readline().split()
        self.grid_min_x = float(line[0])
        self.grid_min_y = float(line[1])
        self.grid_max_x = float(line[2])
        self.grid_max_y = float(line[3])
        self.ncomp = ncomp

        # find the number of points in the grid
        line = f.readline().split()
        self.grid_n_x = int(line[0])
        self.grid_n_y = int(line[1])
        self.k_limit = int(line[2])

        self.grid_step_x = (self.grid_max_x - self.grid_min_x) / (self.grid_n_x - 1)
        self.grid_step_y = (self.grid_max_y - self.grid_min_y) / (self.grid_n_y - 1)

        # We can now initialise the numpy arrays to hold the field data
        self.field = numpy.zeros(shape=(self.grid_n_x, self.grid_n_y, self.ncomp), dtype=numpy.complex)

        for j in range(self.grid_n_y):
            # If k_limit is 1 then rows of grid are sparse (i.e. limited length)
            # read the limits from each line before reading in data
            if self.k_limit == 1:
                line = f.readline().split()
                i_s = int(line[0]) - 1
                i_e = i_s + int(line[1])
            else:
                i_s = 0
                i_e = self.grid_n_x

            # Read in the data
            for i in range(i_s, i_e):
                line = f.readline().split()
                if self.ncomp == 2:
                    self.field[j, i, 0] = complex(float(line[0]), float(line[1]))
                    self.field[j, i, 1] = complex(float(line[2]), float(line[3]))
                else:
                    self.field[j, i, 0] = complex(float(line[0]), float(line[1]))
                    self.field[j, i, 1] = complex(float(line[2]), float(line[3]))
                    self.field[j, i, 2] = complex(float(line[4]), float(line[5]))

        return 0

    def index_radial_dist(self, i, j):
        """Return radial distance from the beam center to an element of the field.

        Useful for calculating the integrated power in a beam within a certain radius."""
        pos_x = self.grid_min_x + self.grid_step_x * i
        pos_y = self.grid_min_y + self.grid_step_y * j

        off_x = pos_x - self.beam_centre[0]
        off_y = pos_y - self.beam_centre[1]

        return numpy.sqrt(off_x ** 2 + off_y ** 2)

    def grid_pos(self):
        """Return meshed grids of the x and y positions of each point in the field"""
        return numpy.meshgrid(numpy.linspace(self.grid_min_x, self.grid_max_x, self.grid_n_x), \
                              numpy.linspace(self.grid_min_y, self.grid_max_y, self.grid_n_y))

    def radius_grid(self, center=None):
        """Return an array holding the radii of each point from the beam centre"""
        grid_x, grid_y = self.grid_pos()

        if center is None:
            center = self.beam_centre

        return numpy.sqrt((grid_x - center[0]) ** 2 + (grid_y - center[1]) ** 2)

    def rotate_polarization(self, angle=45.0):
        """Rotate the basis of the polarization by <angle>"""
        ang = numpy.deg2rad(angle)
        output0 = self.field[:, :, 0] * numpy.cos(ang) - self.field[:, :, 1] * numpy.sin(ang)
        output1 = self.field[:, :, 1] * numpy.cos(ang) + self.field[:, :, 0] * numpy.sin(ang)
        self.field[:, :, 0] = output0
        self.field[:, :, 1] = output1


# The main file object class
class GraspGrid:
    """Object holding the data in contained in a general Grasp grid field output"""

    def __init__(self):
        """Create empty variables or lists of attributes for holding data for each dataset"""
        # Text Header
        self.header = ""

        # File Type parameters
        self.ktype = 0  # type of file format
        self.nset = 0  # number of datasets
        self.icomp = 0  # type of field components
        self.ncomp = 0  # number of field components
        self.igrid = 0  # grid type

        self.freqs = None
        # List of field objects
        self.fields = []
        self.beam_centers = []

    def read_grasp_grid(self, fi):
        """Reads GRASP output grid files from file object and fills a number of variables
        and numpy arrays with the data"""

        # Loop over initial lines before "++++" getting text
        self.header = ""

        while 1:
            line = fi.readline()
            if line[0:4] == "++++":
                break
            else:
                self.header = self.header + line

        # Parse the header to get the frequency information
        for line in self.header.split("\n"):
            term, arg, res = line.partition(":")
            # print term
            if term.strip() == "FREQUENCY":
                # print line
                first, arg, rest = res.partition(":")
                if first.strip() == "start_frequency":
                    # print rest
                    # We have a frequency range
                    start, stop, num_freq = rest.rsplit(",")
                    self.freqs = numpy.linspace(float(start.split()[0]), float(stop.split()[0]), int(num_freq))
                else:
                    # We probably have a list of frequencies
                    # print res
                    freq_strs = res.rsplit("'")
                    freqs = []
                    for f in freq_strs:
                        freqs.append(float(f.split()[0]))
                    self.freqs = numpy.array(freqs)
                break

        # We've now got through the header text and are ready to read the general
        # field type parameters
        self.ktype = int(fi.readline())
        line = fi.readline().split()
        self.nset = int(line[0])
        self.icomp = int(line[1])
        self.ncomp = int(line[2])
        self.igrid = int(line[3])

        self.beam_centers = []
        for i in range(self.nset):
            line = fi.readline().split()
            self.beam_centers.append([int(line[0]), int(line[1])])

        # field type parameters are now understood
        # we now start reading the individual fields
        for i in range(self.nset):
            dataset = GraspField()
            dataset.beamCenter = self.beam_centers[i]
            dataset.read_grasp_field(fi, self.ncomp)
            self.fields.append(dataset)

    def rotate_polarization(self, angle=45.0):
        """Rotate the polarization basis for each field in the GraspGrid"""
        for f in self.fields:
            f.rotate_polarization(angle)
