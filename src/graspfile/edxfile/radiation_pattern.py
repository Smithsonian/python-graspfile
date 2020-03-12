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
from graspfile import numpy_utilities as nu
from io import StringIO, IOBase

from matplotlib import pyplot as pp


class RadiationPattern:
    """Class to parse and hold data from a CHAMP .edx output file."""

    def __init__(self, file_like=None):
        """Create a RadiationPattern object, reading and parsing from <file>.

        if file not given, create empty object to be filled with .read, etc."""
        # Flag to prevent errors from calling methods on objects with no data
        self.__ready = False

        self._tree = None
        self._root = None

        self._shape = None

        self.nComponents = 0
        self.componentType = None
        self.nPhi = 0
        self.phi = None
        self.frequency = None
        self._radPat = None

        if file_like:
            self.read(file_like)

    def read(self, f):
        """Read and parse a .edx file

        f can be either a file name or a file object"""
        if isinstance(f, IOBase):
            file_like = f
        else:
            file_like = open(f)

        # Start by parsing xml
        # huge_tree prevents errors due to large text nodes.  There is some security risk to this,
        # but it is unavoidable in this application
        p = etree.XMLParser(huge_tree=True)
        self._tree = etree.parse(file_like, p)
        self._root = self._tree.getroot()

        # Now start filling attributes read from file

        # Read the shape of the radiation pattern data
        rad_pat_shape_text = self._root.find(
            '{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="SpherCut_RadiationPattern"]/{http://www.edi-forum.org}Sizes').text
        rad_pat_shape = []

        # Read and manipulate shape to allow for complex numbers
        for i in rad_pat_shape_text.strip().split():
            rad_pat_shape.append(int(i))
        rad_pat_shape.append(2)

        self._shape = rad_pat_shape

        # Read the field component number and type
        self.nComponents = int(self._root.find(
            '{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="SpherCut_ProjectionComponents"]/{http://www.edi-forum.org}Sizes').text)
        self.componentType = self._root.find(
            '{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="SpherCut_ProjectionComponents"]').attrib[
            "Class"].split(':')[1]

        # Read the phi cut values
        self.nPhi = int(self._root.find(
            '{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="SpherCut_Phi"]/{http://www.edi-forum.org}Sizes').text)
        phi_element = self._root.find(
            '{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="SpherCut_Phi"]/{http://www.edi-forum.org}Component/{http://www.edi-forum.org}Value')
        phi_text = StringIO(phi_element.text)
        self.phi = np.loadtxt(phi_text)

        # Read the theta values
        theta_element = self._root.find(
            '{http://www.edi-forum.org}Data/{http://www.edi-forum.org}Variable[@Name="SpherCut_Theta"]/{http://www.edi-forum.org}Component/')
        theta_text = StringIO(theta_element.text)
        self.theta = np.loadtxt(theta_text)

        # Read the frequency vector
        freq_element = self._root.find(
            '{http://www.edi-forum.org}Declarations/{http://www.edi-forum.org}Folder/{http://www.edi-forum.org}Variable[@Name="SpherCut_Frequency"]/{http://www.edi-forum.org}Component/')
        freq_text = StringIO(freq_element.text)
        self.frequency = np.loadtxt(freq_text)

        # Now read the actual data
        rad_pat_element = self._root.find(
            '{http://www.edi-forum.org}Data/{http://www.edi-forum.org}Variable[@Name="SpherCut_RadiationPattern"]/{http://www.edi-forum.org}Component/')
        rad_pat_text = StringIO(rad_pat_element.text)
        raw_rad_pat = np.loadtxt(rad_pat_text)
        rad_pats = raw_rad_pat.reshape(rad_pat_shape)
        self._radPat = rad_pats[:, :, :, :, 0] + 1j * rad_pats[:, :, :, :, 1]

        # Should now have all data from file

    def from_grasp_cut(self, grasp_cut_file, freqs):
        """Fill the Radiation Pattern object from a Grasp Cut File"""
        self.nComponents = grasp_cut_file.cutSets[0].cuts[0].field_components

        if grasp_cut_file.cutSets[0].cuts[0].polarization == 3:
            self.componentType = "Ludwig3"
        # Additional switches needed here.

        self.nPhi = len(grasp_cut_file.cutSets[0].cuts)
        self.phi = np.zeros(self.nPhi, dtype=float)

        self.theta = np.linspace(grasp_cut_file.cutSets[0].cuts[0].v_ini,
                                 grasp_cut_file.cutSets[0].cuts[0].v_ini + grasp_cut_file.cutSets[0].cuts[0].v_inc * (
                                     grasp_cut_file.cutSets[0].cuts[0].v_num - 1),
                                 grasp_cut_file.cutSets[0].cuts[0].v_num)

        self.frequency = freqs

        n_freq = len(grasp_cut_file.cutSets)
        n_cuts = len(grasp_cut_file.cutSets[0].cuts)
        n_cut_idx = len(self.theta)

        self._shape = [self.nComponents, n_cuts, n_cut_idx, n_freq]

        self._radPat = np.zeros(self._shape, dtype=np.complex)

        for f, s in enumerate(grasp_cut_file.cutSets):  # Loop over frequency
            for p, cut in enumerate(s.cuts):  # Loop over phi
                self.phi[p] = cut.constant
                for i in range(self.nComponents):
                    self._radPat[i, p, :, f] = cut.data[:]['f{:d}'.format(i + 1)]

    def rotate_polarization(self, angle=45.0):
        """Rotate the basis of the polarization by <angle>"""
        ang = np.deg2rad(angle)
        output0 = self._radPat[0, :, :, :] * np.cos(ang) - self._radPat[1, :, :, :] * np.sin(ang)
        output1 = self._radPat[1, :, :, :] * np.cos(ang) + self._radPat[0, :, :, :] * np.sin(ang)
        self._radPat[0, :, :, :] = output0
        self._radPat[1, :, :, :] = output1

    def get_pattern_by_freq(self, freq):
        """Return the radiation pattern at one frequency in frequency vector"""
        # Get the index of the nearest frequency in the frequency vector
        freq_idx = nu.find_nearest_idx(self.frequency, freq)

        return self._radPat[:, :, :, freq_idx]

    def get_pattern(self, component, phi, freq):
        """Return an individual radiation pattern for one component, cut angle and frequency"""
        freq_idx = nu.find_nearest_idx(self.frequency, freq)
        phi_idx = nu.find_nearest_idx(self.phi, phi)

        return self._radPat[component, phi_idx, :, freq_idx]

    def get_value(self, component, phi, theta, freq):
        """Return the value of the component of the field at the requested angle and frequency."""
        freq_idx = nu.find_nearest_idx(self.frequency, freq)
        theta_idx = nu.find_nearest_idx(self.theta, theta)
        phi_idx = nu.find_nearest_idx(self.phi, phi)

        return self._radPat[component, phi_idx, theta_idx, freq_idx]

    def plot_pattern_dB(self, component, phi, freq, apert_scale=1.0, label=None, norm=False, **kwargs):
        """Convenience function to plot an individual radiation pattern for one component, cut angle and frequency

        apert_scale Aperture scaling contains the relative size of the aperture to scale to. Angles are scaled by 1/factor
        and amplitude is scaled by factor. This is provided to allow systems with different apertures to be compared."""
        rad_pat = self.get_pattern(component, phi, freq)

        phi = nu.find_nearest(self.phi, phi)
        freq = nu.find_nearest(self.frequency, freq)

        if label is None:
            label = r"Component {:d}, $\phi={:g}^\circ$, {:g} GHz".format(component, phi, freq / 1.0e9)
        zp = 0
        if norm:
            zp = 20 * np.log10(np.abs(rad_pat[nu.find_nearest_idx(self.theta, 0)]))
        pp.plot(self.theta / apert_scale, 20 * np.log10(apert_scale * np.abs(rad_pat)) - zp, label=label, **kwargs)

    def plot_pattern_phase(self, component, phi, freq, apert_scale=1.0, label=None, norm=False, **kwargs):
        """Convenience function to plot an individual radiation pattern for one component, cut angle and frequency

        apert_scale Aperture scaling contains the relative size of the aperture to scale to. Angles are scaled by 1/factor.
        This is provided to allow systems with different apertures to be compared."""
        rad_pat = self.get_pattern(component, phi, freq)

        phi = nu.find_nearest(self.phi, phi)
        freq = nu.find_nearest(self.frequency, freq)

        if label is None:
            label = r"Component {:d}, $\phi={:g}^\circ$, {:g} GHz".format(component, phi, freq / 1.0e9)
        zp = 0
        if norm :
            zp = np.angle(rad_pat[nu.find_nearest_idx(self.theta, 0)])
        pp.plot(self.theta, np.rad2deg(np.angle(rad_pat) - zp), label=label, **kwargs)

    def find_peak_value(self, component, phi, freq, apert_scale=1.0, min_theta=-90.0, max_theta=90.0):
        """Find and return the peak value of the field component in the given phi cut"""
        peak_theta = self.find_peak_theta(component, phi, freq, min_theta=min_theta, max_theta=max_theta)
        return self.get_value(component, phi, peak_theta, freq)

    def find_peak_theta(self, component, phi, freq, min_theta=-90.0, max_theta=90.0):
        """Find the theta value at which the field component in the requested field cut is maximum"""
        pattern = self.get_pattern(component, phi, freq)
        # Find the peak of a field
        theta = self.theta

        f = np.abs(pattern)
        if max_theta is not None:
            tmask = ma.masked_greater(theta, max_theta)
            f = ma.array(f, mask=tmask.mask)

        if max_theta is not None:
            tmask = ma.masked_less(theta, min_theta)
            f = ma.array(f, mask=tmask.mask)

        nx = np.unravel_index(np.argmax(abs(f)), f.shape)
        x_peak = theta[nx]

        return x_peak
