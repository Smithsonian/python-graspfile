#!/usr/bin/env python
#
# GRASP_cut.py
#
# P. Grimes, March 2009
#
# Class to read, write and manipulate GRASP cut files
#

import string
import GraspFile.GraspCut as GraspCut

class GraspCutSet:
    """Class for containing a set of cuts with a common parameter, such as
    frequency, beam, etc."""
    def __init__(self):
        self.cuts = []


class GraspCutFile:
    """Class for reading, holding, manipulating and writing GRASP 9.3 format
    output cut files"""
    def __init__(self):
        self.filename = ""
        self.cutSets = [GraspCutSet()]
        self.cut_type = "spherical"

    def read(self, filename):
        '''Open filename, read the contents and parse into cut objects'''
        self.filename = filename
        file = open(self.filename)
        text = file.readlines()

        self.constants = []  # Constants contains a list of constants (typically phi angles)
                        # When values are repeated, it indicates that a second set of cuts is
                        # in the file
        cutSet = 0
        temp_text = []
        # Read through the file, splitting the lines into separate cuts
        for line in text:
            if line[0:5] == "Field":
                # We have the start of a new cut
                # Have we already collected a cut?
                if temp_text != []:
                    # Create new cut
                    new_cut = GraspCut.GraspCut()
                    new_cut.read(temp_text)
                    if new_cut.constant in self.constants:
                        # We must start a new cutSet
                        self.cutSets.append(GraspCutSet())
                        cutSet += 1
                        self.constants = []
                    self.cutSets[cutSet].cuts.append(new_cut)
                    self.constants.append(new_cut.constant)
                    temp_text = []

            temp_text.append(line)

        # Append the last cut to the file
        if temp_text !=[]:
            new_cut = GraspCut.GraspCut()
            new_cut.read(temp_text)
            self.cutSets[cutSet].cuts.append(new_cut)
            self.constants.append(new_cut.constant)

        file.close()


    def selectPosRange(self, pos_min, pos_max):
        '''Return a new cut file object containing only the parts of
        each cut between pos_min and pos_max inclusive'''
        newcf = GraspCutFile()
        newcf.filename = self.filename
        newcf.cut_type = "spherical"
        for cut in self.cuts:
            newcf.cuts.append(cut.selectPosRange(pos_min, pos_max))

        return newcf
