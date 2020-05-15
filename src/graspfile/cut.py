"""This is the module for manipulating cut files containing one or more field cuts from TICRA Tools, GRASP and CHAMP
"""

import math

import numpy


class GraspSingleCut:
    """Class for reading, holding, manipulating and writing GRASP 9.3 format
    output cuts."""

    def __init__(self):
        self.text = ""
        """str: Cut description."""

        self.cut_type = 1
        """int: Cut type.
            Describes the type of cut.
            No GRASP equivalent

            Values signify:
                * `1`: Spherical cut
                * `2`: Planar or surface cut
                * `3`: Cylindrical cut"""

        self.v_ini = 0
        """float: Initial value of variable that cut is swept over.
            GRASP Parameter V_INI"""

        self.v_inc = 1
        """float: Increment of variable that cut is swept over.
            GRASP Parameter V_INI"""

        self.v_num = 1
        """int: Number of steps for variable that cut is swept over.
            GRASP Parameter V_NUM"""

        self.constant = 0.0
        """float: Constant variable for cut.
            GRASP Parameter C

            definition determined by ICUT."""

        self.icut = 1
        """int: Cut definition.
            GRASP Parameter ICUT

            Values signify the following cut definitions:
                For spherical cuts:
                    * `1`: Standard polar cut with fixed phi
                    * `2`: Conical cut with fixed theta

                For planar and surface cut
                    * `1`: Radial cut with fixed phi and variable distance rho
                    * `2`: Circular cut at fixed rho and variable phi

                For cylindrical cut
                    * `1`: axial cut with fixed phi and variable z
                    * `2`: circular cut with fixed z and variable phi"""

        self.polarization = 3
        """int: Polarization definition for the cut.
            GRASP Parameter ICOMP

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

        self.field_components = 2
        """int: Number of field components
            GRASP Parameter NCOMP

            Value signifies:
                * `2`: for far field
                * `3`: for near field.  3rd component is always E_z"""

        self.data = numpy.ndarray((0, 0))
        """numpy.ndarray: Cut Data as complex array of field components.

        Shape of array is ``(v_num, field_components)``"""

    def read(self, lines):
        """Read cut from lines of text and parse as a cut, filing the
        parameters and data"""
        # Get the specification of the cut and parse it
        specline = lines.pop(0)
        specs = specline.split()

        # Make sure a stray comment line hasn't made it in at the start
        if specs[0] == "Field":
            if len(lines) != 0:
                specline = lines.pop(0)
                specs = specline.split()
            else:
                return

        self.v_ini = float(specs[0])
        self.v_inc = float(specs[1])
        self.v_num = int(specs[2])
        self.constant = float(specs[3])
        self.polarization = int(specs[4])
        self.icut = int(specs[5])
        self.field_components = int(specs[6])

        # Create the numpy structured array for the data
        self.data = numpy.zeros((self.v_num, self.field_components), dtype=complex)

        # Parse lines
        for i in range(self.v_num):
            lline = lines[i].split()
            if lline[0] == "Field":
                continue
            self.data[i, 0] = complex(float(lline[0]), float(lline[1]))
            self.data[i, 1] = complex(float(lline[2]), float(lline[3]))
            if self.field_components == 3:
                self.data[i, 2] = complex(float(lline[4]), float(lline[5]))

    @property
    def positions(self):
        """``numpy.array``: the positions of the data points in the cut file"""
        indices = numpy.arange(self.v_num, dtype=float)
        return self.v_ini + self.v_inc*indices

    def write(self):
        """Write local arrays to disk in GRASP cut file format"""
        pass

    def select_pos_range(self, pos_min, pos_max):
        """Returns a cut containing only the positions between pos_min
        and pos_max inclusive"""
        output = GraspSingleCut()

        output.text = self.text
        output.cut_type = self.cut_type

        output.v_ini = pos_min
        output.v_inc = self.v_inc
        output.v_num = math.ceil((pos_max - pos_min) / self.v_inc)
        output.constant = self.constant
        output.polarization = self.polarization
        output.icut = self.icut
        output.field_components = self.field_components

        # Find the indices of points just within the pos_min and pos_max
        # limits
        i_min = 0
        i_max = self.data.shape[0]
        for d in range(self.data.shape[0]):
            if self.positions[d] >= pos_min:
                if i_min == 0:
                    i_min = d
            if self.positions[d] >= pos_max:
                if i_max > d:
                    i_max = d

        # Set v_ini and v_num
        output.v_ini = self.positions[i_min]
        output.v_num = i_max - i_min + 1

        # Set data
        output.data = self.data[i_min:i_max, :]

        return output


class GraspCutSet:
    """Class for containing a set of cuts with a common parameter, such as
    frequency, beam, etc."""

    def __init__(self):
        self.cuts = []
        """list: List of :class:`.GraspCut` objects in the set."""


class GraspCut:
    """Class for reading, holding, manipulating and writing GRASP 9.3 format
    output cut files.

    A file may contain multiple sets of cuts (e.g. at different frequencies), with each set having several cuts with
    varying constant coordinate value (e.g. phi in a theta-phi grid).

    It's common for GRASP cut files to not contain information on the distinguishing parameter between cut sets,
    particular for cut file output from CHAMP calculations.  The user will have to supply this information, by e.g.
    creating a ``.frequencies`` list as an attributes to this object that stores the necessary information."""

    def __init__(self):
        self.cut_sets = []
        """list: List of :class:`.GraspCutSet`, each representing a set of cuts within the file"""

        self.cut_type = "spherical"
        """str: Describes the type of cut represented in the file.
        Options are:
            * ``spherical``: a cut defined on the surface of a sphere
            * ``planar``: a cut defined on a planar surface or the surface of a reflector
            * ``cylindrical``: a cut defined on the surface of a cylinder"""

        self.constants = []
        """list: A list of the constant values for each cut in each of the sets of cuts."""

    def read(self, fi):
        """Read the contents from filelike fi and parse into cut objects"""
        text = fi.readlines()

        self.constants = []
        # Constants contains a list of constants (typically phi angles)
        # When values are repeated, it indicates that a second set of cuts is
        # in the file

        self.cut_sets.append(GraspCutSet())
        cut_set = 0
        temp_text = []
        # Read through the file, splitting the lines into separate cuts
        for line in text:
            if len(line.split()) == 7:
                # We have the start of a new cut
                # Have we already collected a cut?
                if len(temp_text) > 2:
                    # Create new cut
                    new_cut = GraspSingleCut()
                    new_cut.read(temp_text)
                    if new_cut.constant in self.constants:
                        # We must start a new cut_set
                        self.cut_sets.append(GraspCutSet())
                        cut_set += 1
                        self.constants = []
                    self.cut_sets[cut_set].cuts.append(new_cut)
                    self.constants.append(new_cut.constant)
                    temp_text = []

            if len(line.strip()) > 0:
                temp_text.append(line)

        # Append the last cut to the file
        if temp_text:
            new_cut = GraspSingleCut()
            new_cut.read(temp_text)
            self.cut_sets[cut_set].cuts.append(new_cut)
            self.constants.append(new_cut.constant)

    def select_pos_range(self, pos_min, pos_max):
        """Return a new cut file object containing only the parts of
        each cut between pos_min and pos_max inclusive"""
        newcf = GraspCut()
        newcf.cut_type = "spherical"
        newcf.constants = self.constants
        for cut_set in self.cut_sets:
            newcs = GraspCutSet()
            for c in cut_set.cuts:
                newcs.cuts.append(c.select_pos_range(pos_min, pos_max))
            newcf.cut_sets.append(newcs)

        return newcf
