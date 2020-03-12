#!/usr/bin/env python
#
# aperture_field.py
#
# P. Grimes, Feb 2018
#
# Class to read, write and manipulate .edx files output by TICRA CHAMP, tailored to ApertureFields
#
# Since the XML schema for this format is not available (www.edi-forum.org is dead), we
# have to handcode the XPaths

from lxml import etree
import numpy as np
from graspfile import numpy_utilities as nu
from io import StringIO, IOBase

from matplotlib import pyplot as pp


class ApertureField(object):
    """Class to parse and hold data from a CHAMP .edx output file."""
    def __init__(self, file_like=None):
        """Create a ApertureField object, reading and parsing from <file>.

        if file not given, create empty object to be filled with .read, etc."""
        #: bool: Flag to prevent errors from calling methods on objects with no data
        self.__ready = False

        self._tree = None
        self._root = None

        self._shape = None

        self.n_components = 0
        self.component_type = None
        self.n_phi = 0
        self.phi = None
        self.z = None
        self.rho = None
        self.frequency = None

        self._aperture_field = None

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
        # Prevent errors due to large text nodes.  There is some security risk to this,
        # but it is unavoidable in this application
        p = etree.XMLParser(huge_tree=True)
        self._tree = etree.parse(file_like, p)
        self._root = self._tree.getroot()

        # Now start filling attributes read from file

        # Read the shape of the radiation pattern data
        aperture_field_shape_text = self._root.find(
            '{http://www.edi-forum.org}Declarations/'
            '{http://www.edi-forum.org}Folder/'
            '{http://www.edi-forum.org}Variable[@Name="PlaneCut_E"]/'
            '{http://www.edi-forum.org}Sizes').text
        aperture_field_shape = []

        # Read and manipulate shape to allow for complex numbers
        for i in aperture_field_shape_text.strip().split():
            aperture_field_shape.append(int(i))
        aperture_field_shape.append(2)

        self._shape = aperture_field_shape

        # Read the field component number and type
        self.n_components = int(self._root.find(
            '{http://www.edi-forum.org}Declarations/'
            '{http://www.edi-forum.org}Folder/'
            '{http://www.edi-forum.org}Variable[@Name="PlaneCut_ProjectionComponents"]/'
            '{http://www.edi-forum.org}Sizes').text)
        self.component_type = self._root.find(
            '{http://www.edi-forum.org}Declarations/'
            '{http://www.edi-forum.org}Folder/'
            '{http://www.edi-forum.org}Variable[@Name="PlaneCut_ProjectionComponents"]'
        ).attrib["Class"].split(':')[1]

        # Read the phi cut values
        self.n_phi = int(self._root.find(
            '{http://www.edi-forum.org}Declarations/'
            '{http://www.edi-forum.org}Folder/'
            '{http://www.edi-forum.org}Variable[@Name="PlaneCut_Phi"]/'
            '{http://www.edi-forum.org}Sizes').text)
        phi_element = self._root.find(
            '{http://www.edi-forum.org}Declarations/'
            '{http://www.edi-forum.org}Folder/'
            '{http://www.edi-forum.org}Variable[@Name="PlaneCut_Phi"]/'
            '{http://www.edi-forum.org}Component/'
            '{http://www.edi-forum.org}Value')
        phi_text = StringIO(phi_element.text)
        self.phi = np.loadtxt(phi_text)

        # Read the z values
        z_element = self._root.find(
            '{http://www.edi-forum.org}Declarations/'
            '{http://www.edi-forum.org}Folder/'
            '{http://www.edi-forum.org}Variable[@Name="PlaneCut_Z"]/'
            '{http://www.edi-forum.org}Component/'
            '{http://www.edi-forum.org}Value')
        z_text = StringIO(z_element.text)
        self.z = np.loadtxt(z_text)

        # Read the rho values
        rho_element = self._root.find(
            '{http://www.edi-forum.org}Data/'
            '{http://www.edi-forum.org}Variable[@Name="PlaneCut_Rho"]/'
            '{http://www.edi-forum.org}Component/')
        rho_text = StringIO(rho_element.text)
        self.rho = np.loadtxt(rho_text)

        # Read the frequency vector
        freq_element = self._root.find(
            '{http://www.edi-forum.org}Declarations/'
            '{http://www.edi-forum.org}Folder/'
            '{http://www.edi-forum.org}Variable[@Name="PlaneCut_Frequency"]/'
            '{http://www.edi-forum.org}Component/')
        freq_text = StringIO(freq_element.text)
        self.frequency = np.loadtxt(freq_text)

        # Now read the actual data
        aperture_field_element = self._root.find(
            '{http://www.edi-forum.org}Data/'
            '{http://www.edi-forum.org}Variable[@Name="PlaneCut_E"]/'
            '{http://www.edi-forum.org}Component/')
        aperture_field_text = StringIO(aperture_field_element.text)
        r_p = np.loadtxt(aperture_field_text)
        aperture_fields = r_p.reshape(aperture_field_shape)
        self._aperture_field = aperture_fields[:, :, :, :, :, 0] + 1j * aperture_fields[:, :, :, :, :, 1]

        # Should now have all data from file

    def rotate_polarization(self, angle=45.0):
        """Rotate the basis of the polarization by <angle>"""
        ang = np.deg2rad(angle)
        output0 = self._aperture_field[0, :, :, :, :] * np.cos(ang) - self._aperture_field[1, :, :, :, :] * np.sin(ang)
        output1 = self._aperture_field[1, :, :, :, :] * np.cos(ang) + self._aperture_field[0, :, :, :, :] * np.sin(ang)
        self._aperture_field[0, :, :, :, :] = output0
        self._aperture_field[1, :, :, :, :] = output1

    def get_pattern_by_freq(self, freq):
        """Return the radiation pattern at one frequency in frequency vector"""
        # Get the index of the nearest frequency in the frequency vector
        freq_idx = nu.findNearestIdx(self.frequency, freq)

        return self._aperture_field[:, :, :, :, freq_idx]

    def get_pattern(self, component, phi, z, freq):
        """Return an individual radiation pattern for one component, cut angle and frequency"""
        freq_idx = nu.findNearestIdx(self.frequency, freq)
        phi_idx = nu.findNearestIdx(self.phi, phi)
        z_idx = nu.findNearestIdx(self.z, z)

        return self._aperture_field[component, :, z_idx, phi_idx, freq_idx]

    def plot_pattern_db(self, component, phi, z, freq, label=None, apert_scale=1.0, **kwargs):
        """Convenience function to plot an individual radiation pattern for one component, cut angle and frequency.

        Setting a apert_scale will multiply the values of rho by that factor, and divide the power density in the field
        by that factor^2"""
        aperture_field = self.get_pattern(component, phi, z, freq)

        phi = nu.findNearest(self.phi, phi)
        freq = nu.findNearest(self.frequency, freq)
        z = nu.findNearest(self.z, z)

        if label is None:
            label = r"Component {:d}, $\phi={:g}^\circ$, z={:g}mm, {:g} GHz".format(component, phi, z * 1e3,
                                                                                    freq / 1.0e9)
        pp.plot(self.rho * apert_scale, 20 * np.log10(np.abs(aperture_field) / apert_scale), label=label, **kwargs)

    def plot_pattern_phase(self, component, phi, z, freq, label=None, apert_scale=1.0, **kwargs):
        """Convenience function to plot an individual radiation pattern for one component, cut angle and frequency

        Setting a apert_scale will multiply the values of rho by that factor"""
        aperture_field = self.get_pattern(component, phi, z, freq)

        phi = nu.findNearest(self.phi, phi)
        freq = nu.findNearest(self.frequency, freq)
        z = nu.findNearest(self.z, z)

        if label is None:
            label = r"Component {:d}, $\phi={:g}^\circ$, z={:g}mm, {:g} GHz".format(component, phi, z * 1e3,
                                                                                    freq / 1.0e9)
        pp.plot(self.rho * apert_scale, np.rad2deg(np.angle(aperture_field) - np.angle(aperture_field[0])), label=label,
                **kwargs)

    def make_single_sided(self):
        """Converts a double sided aperture field (rho running from -a to +a, phi=0 to phi=180 def)
        to a single side field (rho running from 0 to a, phi=0 to 360)"""
        new_rho = self.rho[int((len(self.rho)) / 2):]
        new_phi = np.concatenate((self.phi[:], self.phi[1:] + 180))
        new_ap_field = np.concatenate((self._aperture_field[:, int(len(self.rho) / 2):, :, :, :],
                                       self._aperture_field[:, int(len(self.rho) / 2)::-1, :, 1:, :]), axis=3)
        self.rho = new_rho
        self.phi = new_phi
        self.n_phi = len(new_phi)
        self._aperture_field = new_ap_field
