#!/usr/bin/env python
#
# ChampApertureFieldEdxFile.py
#
# P. Grimes, Feb 2018
#
# Class to read, write and manipulate .edx files output by TICRA CHAMP, tailored to ApertureFields
#
# Since the XML schema for this format is not available (www.edi-forum.org is dead), we
# have to handcode the XPaths

from lxml import etree
import numpy as np
import NumpyUtility as nu
from io import StringIO, IOBase

from matplotlib import pyplot as pp


class ApertureField:
    """Class to parse and hold data from a CHAMP .edx output file."""

    def __init__(self, fileLike=None):
        """Create a ApertureField object, reading and parsing from <file>.

        if file not given, create empty object to be filled with .read, etc."""
        # Flag to prevent errors from calling methods on objects with no data
        self.__ready = False

        if fileLike:
            self.read(fileLike)

    def read(self, f):
        """Read and parse a .edx file

        f can be either a file name or a file object"""
        if isinstance(f, IOBase):
            fileLike = f
        else:
            fileLike = open(f)

        # Start by parsing xml
        # Prevent errors due to large text nodes.  There is some security risk to this,
        # but it is unavoidable in this application
        p = etree.XMLParser(huge_tree=True)
        self._tree = etree.parse(fileLike, p)
        self._root = self._tree.getroot()

        # Now start filling attributes read from file

        # Read the shape of the radiation pattern data
        apertureFieldShapeText = self._root.find(
            '{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="PlaneCut_E"]/{http://www.edi-forum.org}Sizes').text
        apertureFieldShape = []

        # Read and manipulate shape to allow for complex numbers
        for i in apertureFieldShapeText.strip().split():
            apertureFieldShape.append(int(i))
        apertureFieldShape.append(2)

        self._shape = apertureFieldShape

        # Read the field component number and type
        self.nComponents = int(self._root.find(
            '{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="PlaneCut_ProjectionComponents"]/{http://www.edi-forum.org}Sizes').text)
        self.componentType = self._root.find(
            '{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="PlaneCut_ProjectionComponents"]').attrib[
            "Class"].split(':')[1]

        ## Read the phi cut values
        self.nPhi = int(self._root.find(
            '{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="PlaneCut_Phi"]/{http://www.edi-forum.org}Sizes').text)
        phiElement = self._root.find(
            '{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="PlaneCut_Phi"]/{http://www.edi-forum.org}Component/{http://www.edi-forum.org}Value')
        phiText = StringIO(phiElement.text)
        self.phi = np.loadtxt(phiText)

        ## Read the z values
        zElement = self._root.find(
            '{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="PlaneCut_Z"]/{http://www.edi-forum.org}Component/{http://www.edi-forum.org}Value')
        zText = StringIO(zElement.text)
        self.z = np.loadtxt(zText)

        ## Read the rho values
        rhoElement = self._root.find(
            '{http://www.edi-forum.org}Data/{http://www.edi-forum.org}Variable[@Name="PlaneCut_Rho"]/{http://www.edi-forum.org}Component/')
        rhoText = StringIO(rhoElement.text)
        self.rho = np.loadtxt(rhoText)

        ## Read the frequency vector
        freqElement = self._root.find(
            '{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="PlaneCut_Frequency"]/{http://www.edi-forum.org}Component/')
        freqText = StringIO(freqElement.text)
        self.frequency = np.loadtxt(freqText)

        # Now read the actual data
        apertureFieldElement = self._root.find(
            '{http://www.edi-forum.org}Data/{http://www.edi-forum.org}Variable[@Name="PlaneCut_E"]/{http://www.edi-forum.org}Component/')
        apertureFieldText = StringIO(apertureFieldElement.text)
        rP = np.loadtxt(apertureFieldText)
        apertureFields = rP.reshape(apertureFieldShape)
        self._apertureField = apertureFields[:, :, :, :, :, 0] + 1j * apertureFields[:, :, :, :, :, 1]

        # Should now have all data from file

    def rotatePolarization(self, angle=45.0):
        '''Rotate the basis of the polarization by <angle>'''
        ang = np.deg2rad(angle)
        output0 = self._apertureField[0, :, :, :, :] * np.cos(ang) - self._apertureField[1, :, :, :, :] * np.sin(ang)
        output1 = self._apertureField[1, :, :, :, :] * np.cos(ang) + self._apertureField[0, :, :, :, :] * np.sin(ang)
        self._apertureField[0, :, :, :, :] = output0
        self._apertureField[1, :, :, :, :] = output1

    def getPatternByFreq(self, freq):
        '''Return the radiation pattern at one frequency in frequency vector'''
        # Get the index of the nearest frequency in the frequency vector
        freqIdx = nu.findNearestIdx(self.frequency, freq)

        return self._apertureField[:, :, :, :, freqIdx]

    def getPattern(self, component, phi, z, freq):
        '''Return an individual radiation pattern for one component, cut angle and frequency'''
        freqIdx = nu.findNearestIdx(self.frequency, freq)
        phiIdx = nu.findNearestIdx(self.phi, phi)
        zIdx = nu.findNearestIdx(self.z, z)

        return self._apertureField[component, :, zIdx, phiIdx, freqIdx]

    def plotPatterndB(self, component, phi, z, freq, label=None, apert_scale=1.0, **kwargs):
        '''Convenience function to plot an individual radiation pattern for one component, cut angle and frequency.

        Setting a apert_scale will multiply the values of rho by that factor, and divide the power density in the field by that factor^2'''
        apertureField = self.getPattern(component, phi, z, freq)

        phi = nu.findNearest(self.phi, phi)
        freq = nu.findNearest(self.frequency, freq)
        z = nu.findNearest(self.z, z)

        if label == None:
            label = r"Component {:d}, $\phi={:g}^\circ$, z={:g}mm, {:g} GHz".format(component, phi, z * 1e3,
                                                                                    freq / 1.0e9)
        pp.plot(self.rho * apert_scale, 20 * np.log10(np.abs(apertureField) / apert_scale), label=label, **kwargs)

    def plotPatternPhase(self, component, phi, z, freq, label=None, apert_scale=1.0, **kwargs):
        '''Convenience function to plot an individual radiation pattern for one component, cut angle and frequency

        Setting a apert_scale will multiply the values of rho by that factor'''
        apertureField = self.getPattern(component, phi, z, freq)

        phi = nu.findNearest(self.phi, phi)
        freq = nu.findNearest(self.frequency, freq)
        z = nu.findNearest(self.z, z)

        if label == None:
            label = r"Component {:d}, $\phi={:g}^\circ$, z={:g}mm, {:g} GHz".format(component, phi, z * 1e3,
                                                                                    freq / 1.0e9)
        pp.plot(self.rho * apert_scale, np.rad2deg(np.angle(apertureField) - np.angle(apertureField[0])), label=label,
                **kwargs)

    def makeSingleSided(self):
        """Converts a double sided aperture field (rho running from -a to +a, phi=0 to phi=180 def)
        to a single side field (rho running from 0 to a, phi=0 to 360)"""
        newRho = self.rho[int((len(self.rho)) / 2):]
        newPhi = np.concatenate((self.phi[:], self.phi[1:] + 180))
        newApField = np.concatenate((self._apertureField[:, int(len(self.rho) / 2):, :, :, :],
                                     self._apertureField[:, int(len(self.rho) / 2)::-1, :, 1:, :]), axis=3)
        self.rho = newRho
        self.phi = newPhi
        self.nPhi = len(newPhi)
        self._apertureField = newApField
