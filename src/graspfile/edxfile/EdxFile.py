#!/usr/bin/env python
#
# ChampEdxFile.py
#
# P. Grimes, March 2018
#
# Class to read, write and manipulate .edx files output by TICRA CHAMP
#
# Since the XML schema for this format is not available (www.edi-forum.org is dead), we
# have to handcode the XPaths

from lxml import etree
import numpy as np
import NumpyUtility as nu
from io import StringIO, IOBase

from matplotlib import pyplot as pp

class EdxFile:
    '''Class to parse and hold data from a CHAMP .edx output file.'''
    def __init__(self, fileLike=None):
        '''Create an EdxFile object, reading and parsing from <file>.

        if file not given, create empty object to be filled with .read, etc.'''
        # Flag to prevent errors from calling methods on objects with no data
        self.__ready = False

        if fileLike !=None:
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
        phiText = StringIO(unicode(phiElement.text))
        self.phi = np.loadtxt(phiText)

        ## Read the theta values
        thetaElement = self._root.find('{http://www.edi-forum.org}Data/{http://www.edi-forum.org}Variable[@Name="SpherCut_Theta"]/{http://www.edi-forum.org}Component/')
        thetaText = StringIO(unicode(thetaElement.text))
        self.theta = np.loadtxt(thetaText)

        ## Read the frequency vector
        freqElement = self._root.find('{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="SpherCut_Frequency"]/{http://www.edi-forum.org}Component/')
        freqText = StringIO(unicode(freqElement.text))
        self.frequency = np.loadtxt(freqText)

        # Now read the actual data
        radPatElement = self._root.find('{http://www.edi-forum.org}Data/{http://www.edi-forum.org}Variable[@Name="SpherCut_RadiationPattern"]/{http://www.edi-forum.org}Component/')
        radPatText = StringIO(unicode(radPatElement.text))
        rP = np.loadtxt(radPatText)
        radPats = rP.reshape(radPatShape)
        self._radPat = radPats[:,:,:,:,0] + 1j*radPats[:,:,:,:,1]

        # Should now have all data from file

    def getPatternByFreq(self, freq):
        '''Return the radiation pattern at one frequency in frequency vector'''
        # Get the index of the nearest frequency in the frequency vector
        freqIdx = nu.findNearestIdx(self.frequency, freq)

        return self._radPat[:,:,:,freqIdx]


    def getPattern(self, component, phi, freq):
        '''Return an individual radiation pattern for one component, cut angle and frequency'''
        freqIdx = nu.findNearestIdx(self.frequency, freq)
        phiIdx = nu.findNearestIdx(self.phi, phi)

        return self._radPat[component,phiIdx,:,freqIdx]

    def plotPatterndB(self, component, phi, freq, label=None):
        '''Convenience function to plot an individual radiation pattern for one component, cut angle and frequency'''
        radPat = self.getPattern(component, phi, freq)

        phi = nu.findNearest(self.phi, phi)
        freq = nu.findNearest(self.frequency, freq)

        if label==None:
            label = r"Component {:d}, $\phi={:g}^\circ$, {:g} GHz".format(component, phi, freq/1.0e9)
        pp.plot(self.theta, 20*np.log10(np.abs(radPat)), label=label)
