#!/usr/bin/env python
#
# ChampRadPatEdxFile.py
#
# P. Grimes, March 2018
#
# Class to read, write and manipulate .edx files output by TICRA CHAMP
#
# Since the XML schema for this format is not available (www.edi-forum.org is dead), we
# have to handcode the XPaths

from lxml import etree
import numpy as np
import numpy.ma as ma
import NumpyUtility as nu
from io import StringIO, IOBase

from matplotlib import pyplot as pp

class RadiationPattern:
    '''Class to parse and hold data from a CHAMP .edx output file.'''
    def __init__(self, fileLike=None):
        '''Create a RadiationPattern object, reading and parsing from <file>.

        if file not given, create empty object to be filled with .read, etc.'''
        # Flag to prevent errors from calling methods on objects with no data
        self.__ready = False

        if fileLike:
            self.read(fileLike)

    def read(self, f):
        '''Read and parse a .edx file

        f can be either a file name or a file object'''
        if isinstance(f, IOBase):
            fileLike = f
        else:
            fileLike = open(f)

        # Start by parsing xml
        ## Prevent errors due to large text nodes.  There is some security risk to this,
        ## but it is unavoidable in this application
        p = etree.XMLParser(huge_tree=True)
        self._tree = etree.parse(fileLike, p)
        self._root = self._tree.getroot()

        # Now start filling attributes read from file

        ## Read the shape of the radiation pattern data
        radPatShapeText = self._root.find('{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="SpherCut_RadiationPattern"]/{http://www.edi-forum.org}Sizes').text
        radPatShape = []

        ### Read and manipulate shape to allow for complex numbers
        for i in radPatShapeText.strip().split():
            radPatShape.append(int(i))
        radPatShape.append(2)

        self._shape = radPatShape

        ## Read the field component number and type
        self.nComponents = int(self._root.find('{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="SpherCut_ProjectionComponents"]/{http://www.edi-forum.org}Sizes').text)
        self.componentType = self._root.find('{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="SpherCut_ProjectionComponents"]').attrib["Class"].split(':')[1]

        ## Read the phi cut values
        self.nPhi = int(self._root.find('{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="SpherCut_Phi"]/{http://www.edi-forum.org}Sizes').text)
        phiElement = self._root.find('{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="SpherCut_Phi"]/{http://www.edi-forum.org}Component/{http://www.edi-forum.org}Value')
        phiText = StringIO(phiElement.text)
        self.phi = np.loadtxt(phiText)

        ## Read the theta values
        thetaElement = self._root.find('{http://www.edi-forum.org}Data/{http://www.edi-forum.org}Variable[@Name="SpherCut_Theta"]/{http://www.edi-forum.org}Component/')
        thetaText = StringIO(thetaElement.text)
        self.theta = np.loadtxt(thetaText)

        ## Read the frequency vector
        freqElement = self._root.find('{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="SpherCut_Frequency"]/{http://www.edi-forum.org}Component/')
        freqText = StringIO(freqElement.text)
        self.frequency = np.loadtxt(freqText)

        # Now read the actual data
        radPatElement = self._root.find('{http://www.edi-forum.org}Data/{http://www.edi-forum.org}Variable[@Name="SpherCut_RadiationPattern"]/{http://www.edi-forum.org}Component/')
        radPatText = StringIO(radPatElement.text)
        rP = np.loadtxt(radPatText)
        radPats = rP.reshape(radPatShape)
        self._radPat = radPats[:,:,:,:,0] + 1j*radPats[:,:,:,:,1]

        # Should now have all data from file

    def fromGraspCut(self, graspCutFile, freqs):
        '''Fill the Radiation Pattern object from a Grasp Cut File'''
        self.nComponents = graspCutFile.cutSets[0].cuts[0].field_components

        if graspCutFile.cutSets[0].cuts[0].polarization == 3:
            self.componentType = "Ludwig3"
        # Additional switches needed here.

        self.nPhi = len(graspCutFile.cutSets[0].cuts)
        self.phi = np.zeros((self.nPhi), dtype=float)

        self.theta = np.linspace(graspCutFile.cutSets[0].cuts[0].v_ini, graspCutFile.cutSets[0].cuts[0].v_ini + graspCutFile.cutSets[0].cuts[0].v_inc*(graspCutFile.cutSets[0].cuts[0].v_num-1), graspCutFile.cutSets[0].cuts[0].v_num)

        self.frequency = apField.frequency

        nFreq = len(graspCutFile.cutSets)
        nCuts = len(graspCutFile.cutSets[0].cuts)
        nCutIdx = len(self.theta)

        self._shape = [self.nComponents, nCuts, nCutIdx, nFreq]

        self._radPat = np.zeros(self._shape, dtype=np.complex)

        for f, s in enumerate(graspCutFile.cutSets):  # Loop over frequency
            for p, cut in enumerate(s.cuts): # Loop over phi
                self.phi[p] = cut.constant
                for i in range(self.nComponents):
                    self._radPat[i, p, :, f] = cut.data[:]['f{:d}'.format(i+1)]

    def rotatePolarization(self, angle=45.0):
        '''Rotate the basis of the polarization by <angle>'''
        ang = np.deg2rad(angle)
        output0 = self._radPat[0,:,:,:]*np.cos(ang)-self._radPat[1,:,:,:]*np.sin(ang)
        output1 = self._radPat[1,:,:,:]*np.cos(ang)+self._radPat[0,:,:,:]*np.sin(ang)
        self._radPat[0,:,:,:] = output0
        self._radPat[1,:,:,:] = output1



    def getPatternByFreq(self, freq):
        '''Return the radiation pattern at one frequency in frequency vector'''
        # Get the index of the nearest frequency in the frequency vector
        freqIdx = nu.findNearestIdx(self.frequency, freq)

        return self._radPat[:,:,:,freqIdx]


    def getPattern(self, component, phi, freq):
        '''Return an individual radiation pattern for one component, cut angle and frequency'''
        freqIdx = nu.findNearestIdx(self.frequency, freq)
        phiIdx = nu.findNearestIdx(self.phi, phi)

        return self._radPat[component, phiIdx,:,freqIdx]

    def getValue(self, component, phi, theta, freq):
        '''Return the value of the component of the field at the requested angle and frequency.'''
        freqIdx = nu.findNearestIdx(self.frequency, freq)
        thetaIdx = nu.findNearestIdx(self.theta, theta)
        phiIdx = nu.findNearestIdx(self.phi, phi)

        return self._radPat[component, phiIdx, thetaIdx, freqIdx]

    def plotPatterndB(self, component, phi, freq, apert_scale=1.0, label=None, norm=False, **kwargs):
        '''Convenience function to plot an individual radiation pattern for one component, cut angle and frequency

        apert_scale Aperture scaling contains the relative size of the aperture to scale to. Angles are scaled by 1/factor
        and amplitude is scaled by factor. This is provided to allow systems with different apertures to be compared.'''
        radPat = self.getPattern(component, phi, freq)

        phi = nu.findNearest(self.phi, phi)
        freq = nu.findNearest(self.frequency, freq)

        if label==None:
            label = r"Component {:d}, $\phi={:g}^\circ$, {:g} GHz".format(component, phi, freq/1.0e9)
        zp = 0
        if norm==True:
            zp = 20*np.log10(np.abs(radPat[nu.findNearestIdx(self.theta, 0)]))
        pp.plot(self.theta/apert_scale, 20*np.log10(apert_scale*np.abs(radPat))-zp, label=label, **kwargs)

    def plotPatternPhase(self, component, phi, freq, apert_scale=1.0, label=None, norm=False, **kwargs):
        '''Convenience function to plot an individual radiation pattern for one component, cut angle and frequency

                apert_scale Aperture scaling contains the relative size of the aperture to scale to. Angles are scaled by 1/factor.
                This is provided to allow systems with different apertures to be compared.'''
        radPat = self.getPattern(component, phi, freq)

        phi = nu.findNearest(self.phi, phi)
        freq = nu.findNearest(self.frequency, freq)

        if label==None:
            label = r"Component {:d}, $\phi={:g}^\circ$, {:g} GHz".format(component, phi, freq/1.0e9)
        zp = 0
        if norm==True:
            zp = np.angle(radPat[nu.findNearestIdx(self.theta, 0)])
        pp.plot(self.theta, np.rad2deg(np.angle(radPat)-zp), label=label, **kwargs)

    def findPeakValue(self, component, phi, freq, apert_scale=1.0, min_theta=-90.0, max_theta=90.0):
        '''Find and return the peak value of the field component in the given phi cut'''
        peakTheta = self.findPeakTheta(component, phi, freq, min_theta=min_theta, max_theta=max_theta)
        return self.getValue(component, phi, peakTheta, freq)

    def findPeakTheta(self, component, phi, freq, min_theta=-90.0, max_theta=90.0):
        '''Find the theta value at which the field component in the requested field cut is maximum'''
        pattern = self.getPattern(component, phi, freq)
        # Find the peak of a field
        theta = self.theta

        f = np.abs(pattern)
        if max_theta != None:
            tmask = ma.masked_greater(theta, max_theta)
            f = ma.array(f, mask=tmask.mask)

        if max_theta != None:
            tmask = ma.masked_less(theta, min_theta)
            f = ma.array(f, mask=tmask.mask)

        nx = np.unravel_index(np.argmax(abs(f)), f.shape)
        xPeak = theta[nx]

        return xPeak
