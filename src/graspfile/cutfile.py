"""This is the module for manipulating cut files containing one or more field cuts from TICRA Tools, GRASP and CHAMP
"""

import graspfile.cut as cut


class GraspCutSet:
    """Class for containing a set of cuts with a common parameter, such as
    frequency, beam, etc."""
    def __init__(self):
        self.cuts = []
        """list: List of :class:`.GraspCut` objects in the set."""


class GraspCutFile:
    """Class for reading, holding, manipulating and writing GRASP 9.3 format
    output cut files"""

    def __init__(self):
        self.filename = ""
        """str: The filename the cuts were read from"""

        self.cut_sets = [GraspCutSet()]
        """list: List of :class:`.GraspCutSet`, each representing a set of cuts within the file"""

        self.cut_type = "spherical"
        """str: Describes the type of cut represented in the file.
        Options are:
            * ``spherical``: a cut defined on the surface of a sphere
            * :``planar``: a cut defined on a planar surface or the surface of a reflector
            * :``cylindrical``: a cut defined on the surface of a cylinder"""

        self.constants = []
        """list: A list of the constant values for each set of cuts."""

    def read(self, filename):
        """Open filename, read the contents and parse into cut objects"""
        self.filename = filename
        file = open(self.filename)
        text = file.readlines()

        self.constants = []
        # Constants contains a list of constants (typically phi angles)
        # When values are repeated, it indicates that a second set of cuts is
        # in the file

        cut_set = 0
        temp_text = []
        # Read through the file, splitting the lines into separate cuts
        for line in text:
            if line[0:5] == "Field":
                # We have the start of a new cut
                # Have we already collected a cut?
                if temp_text != []:
                    # Create new cut
                    new_cut = cut.GraspCut()
                    new_cut.read(temp_text)
                    if new_cut.constant in self.constants:
                        # We must start a new cut_set
                        self.cut_sets.append(GraspCutSet())
                        cut_set += 1
                        self.constants = []
                    self.cut_sets[cut_set].cuts.append(new_cut)
                    self.constants.append(new_cut.constant)
                    temp_text = []

            temp_text.append(line)

        # Append the last cut to the file
        if temp_text != []:
            new_cut = cut.GraspCut()
            new_cut.read(temp_text)
            self.cut_sets[cut_set].cuts.append(new_cut)
            self.constants.append(new_cut.constant)

        file.close()

    def select_pos_range(self, pos_min, pos_max):
        """Return a new cut file object containing only the parts of
        each cut between pos_min and pos_max inclusive"""
        newcf = GraspCutFile()
        newcf.filename = self.filename
        newcf.cut_type = "spherical"
        newcf.constants = self.constants
        for cut_set in self.cut_sets:
            newcs = GraspCutSet()
            for c in newcs.cuts:
                newcs.cuts.append(c.select_pos_range(pos_min, pos_max))
            newcf.cut_sets.append(newcs)

        return newcf
