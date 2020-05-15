"""This is the module for manipulating grid files containing one or more field cuts from TICRA Tools, GRASP and CHAMP
"""

import numpy


class GraspField:
    """Object holding a single dataset from a Grasp field on grid output file (``*.grd``)

    The field is held in a complex numpy array of shape ``(grid_n_x, grid_n_y, field_components)``
    where ``grid_n_x`` and ``grid_n_y`` set the number of points in the grid and ``field_components`` is the
    number of field components"""

    # This layout of array should mean that the polarisation components for a point
    # are contiguous memory, allowing rapid calculation of stokes parameters, etc.

    def __init__(self):
        # initialize storage variables
        self.beam_center = [0.0, 0.0]
        """list: Beam center in [x,y] form"""

        # Grid parameters
        self.grid_min_x = 0.0
        """float: Minimum extent of grid in 1st dimension"""

        self.grid_min_y = 0.0
        """float: Minimum extent of grid in 2nd dimension"""

        self.grid_max_x = 0.0
        """float: Maximum extent of grid in 1st dimension"""

        self.grid_max_y = 0.0
        """float: Maximum extent of grid in 2nd dimension"""

        self.grid_n_x = 0
        """int: Number of points in grid in 1st dimension"""

        self.grid_n_y = 0
        """int: Number of points in grid in 2nd dimension"""

        self.grid_step_x = 0.0
        """float: step size of grid in 1st dimension"""

        self.grid_step_y = 0.0
        """float: step size of grid in 2nd dimension"""

        self.k_limit = 0  # Is grid sparse (0=filled, 1=sparse)
        """int: defines whether grid is filled or sparse
            * 0: filled
            * 1: sparse"""

        self.field_components = 0
        """Number of field components in grid.

            Equivalent to the GRASP Grid file's ``ncomp``.
            ``2`` for far fields, ``3`` for near fields."""

        self.field = None
        """numpy.ndarray: the array of complex field components.
            the field object is numpy array of shape ``(grid_n_x, grid_n_y, field_components)``"""

    def read(self, f, field_components):
        """Reads the Grasp dataset from the file object passed in.  This assumes that
        it is being called from the graspGrid classes read(f) method, so that
        the file object is already at the start of the record"""

        # find the grid physical extents
        line = f.readline().split()
        self.grid_min_x = float(line[0])
        self.grid_min_y = float(line[1])
        self.grid_max_x = float(line[2])
        self.grid_max_y = float(line[3])
        self.field_components = field_components

        # find the number of points in the grid
        line = f.readline().split()
        self.grid_n_x = int(line[0])
        self.grid_n_y = int(line[1])
        self.k_limit = int(line[2])

        self.grid_step_x = (self.grid_max_x - self.grid_min_x) / (self.grid_n_x - 1)
        self.grid_step_y = (self.grid_max_y - self.grid_min_y) / (self.grid_n_y - 1)

        # We can now initialise the numpy arrays to hold the field data
        self.field = numpy.zeros(shape=(self.grid_n_x, self.grid_n_y, self.field_components), dtype=numpy.complex)

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
                if self.field_components == 2:
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

        off_x = pos_x - self.beam_center[0]
        off_y = pos_y - self.beam_center[1]

        return numpy.sqrt(off_x ** 2 + off_y ** 2)

    @property
    def positions(self):
        """Return meshed grids of the x and y positions of each point in the field"""
        return numpy.meshgrid(numpy.linspace(self.grid_min_x, self.grid_max_x, self.grid_n_x),
                              numpy.linspace(self.grid_min_y, self.grid_max_y, self.grid_n_y))

    def radius_grid(self, center=None):
        """Return an array holding the radii of each point from the beam centre.

        Args:
            center: tuple holding coordinates of the center to calculate the radius from

        Returns:
            numpy.ndarray: numpy array with same shape as the field grid holding the radii.
        """
        grid_x, grid_y = self.positions

        if center is None:
            center = self.beam_center

        return numpy.sqrt((grid_x - center[0]) ** 2 + (grid_y - center[1]) ** 2)

    def rotate_polarization(self, angle=45.0):
        """Rotate the basis of the polarization by <angle>. Will only work on linear polarization types

        ***TODO: Implement checks for polarization type***

        Args:
            angle: angle in degrees to rotate the polarization basis by.

        Returns:
            nothing.
        """
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
        self.header = []
        """list of str: List of lines in the header section of the file"""

        # File Type parameters
        self.ktype = 1
        """int: type of file format.

        Always ``1`` for TICRA Tools files."""

        self.nset = 0
        """int: number of grids in file."""

        self.polarization = 0
        """int: type of field components.

        Equivalent to the GRASP Grid file's ``icomp``.

        Values signify the following polarization definitions
            * `1`: Linear E_theta and E_phi.
            * `2`: Right hand and left hand circular (Erhc and Elhc).
            * `3`: Linear Eco and Ecx (Ludwig's third definition).
            * `4`: Linear along major and minor axes of the polarisation ellipse, Emaj and Emin.
            * `5`: XPD fields: E_theta/E_phi and E_phi/E_theta.
            * `6`: XPD fields: Erhc/Elhc and Elhc/Erhc.
            * `7`: XPD fields: Eco/Ecx and Ecx/Eco.
            * `8`: XPD fields: Emaj/Emin and Emin/Emaj.
            * `9`: Total power \\|E\\| and Erhc=Elhc."""

        self.field_components = 0
        """int: number of field components.

        Equivalent to the GRASP Grid file's ``ncomp``.
        ``2`` for far fields, ``3`` for near fields."""

        self.igrid = 0
        """int: grid type.

        Type of field grid.
        * `1` : uv-grid: (X; Y ) = (u; v) where u and v are the two first coordinates of the unit vector to the field
                point. Hence, r^ = u; v; p = √(1 − u² − v²) where u and v are related to the spherical angles by
                u = sin θ cos φ; v = sin θ sin φ.
        * `4` : Elevation over azimuth: (X; Y )=(Az,El), where Az and El define the direction to the field point by
                r^ = − sin Az cos El; sin El; cos Az cos El.
        * `5` : Elevation and azimuth: (X; Y )=(Az,El), where Az and El define the direction to the field point through
                the relations Az = -θ cos φ; El = θ sin φ to the spherical angles θ and φ.
        * `6` : Azimuth over elevation: (X; Y )= (Az, El), where Az and El define the direction to the field point by
                r^ = − sin Az; cos Az sin El; cos Az cos El.
        * `7` : θφ-grid: (X; Y ) = (φ; θ), where θ and φ are the spherical angles of the direction to the field point.
        * `9` : Azimuth over elevation, EDX definition: (X; Y )=(Az,El), where Az and El define the direction to the
                field point by r^ = sin Az cos El; sin El; cos Az cos El.
        * `10` : Elevation over azimuth, EDX definition: (X; Y )= (Az, El), where Az and El define the direction to the
                field point by r^ = sin Az; cos Az sin El; cos Az cos El.
        """

        self.freqs = []
        """list: List of frequencies in units of ``freq_unit``"""

        self.freq_unit = ""
        """str: The unit that the frequencies are given in."""

        self.fields = []
        """list of (:obj:`GraspField`): List of individual fields in file,"""

        self.beam_centers = []
        """list: list of beam centers for individual fields in the file."""

    def read(self, fi):
        """Reads GRASP output grid files from file object and fills a number of variables
        and numpy arrays with the data"""

        # Loop over initial lines before "++++" getting text
        self.header = []

        while 1:
            line = fi.readline()
            if line[0:4] == "++++":
                break
            else:
                self.header.append(line)

        # Parse the header to get the frequency information
        for (l, line) in enumerate(self.header):
            term, arg, res = line.partition(":")
            if term.strip() == "FREQUENCY":
                # This works for TICRA GRASP version before TICRA Tools
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
            elif term.strip().split()[0] == "FREQUENCIES":
                # This works for TICRA Tools versions > 19.0
                #
                # If the frequency list is long, it may spread over more than one line
                self.freq_unit = term.strip().split()[1].strip("[]")

                freq_str_list = "  ".join(self.header[l+1:]).split()
                freqs = []
                for f in freq_str_list:
                    freqs.append(float(f))
                self.freqs = numpy.array(freqs)

        # We've now got through the header text and are ready to read the general
        # field type parameters
        self.ktype = int(fi.readline())
        line = fi.readline().split()
        self.nset = int(line[0])
        self.polarization = int(line[1])
        self.field_components = int(line[2])
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
            dataset.read(fi, self.field_components)
            self.fields.append(dataset)

    def rotate_polarization(self, angle=45.0):
        """Rotate the polarization basis for each field in the GraspGrid"""
        for f in self.fields:
            f.rotate_polarization(angle)
