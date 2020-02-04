#!/usr/bin/env python
#
# GRASP_cut.py
#
# P. Grimes, March 2009
#
# Class to read, write and manipulate GRASP cuts
#

import cmath, numpy, math


class GraspCut:
    """Class for reading, holding, manipulating and writing GRASP 9.3 format 
    output cuts"""
    def __init__(self):
        # Cut description
        self.text = ""
                
        # Cut type
        # No GRASP equivalent
        # =1 Spherical cut
        # =2 Planar or surface cut
        # =3 Cylindrical cut
        self.cut_type = 1
        
        # Variable that cut is swept over
        # GRASP Parameter V_INI, V_INC, V_NUM
        self.v_ini = 0
        self.v_inc = 1
        self.v_num = 1
        
        # Fixed variables
        #
        # Constant variable for cut
        # GRASP Parameter C
        #  definition determined by ICUT
        self.constant = 0.0
        
        # Cut definition
        # GRASP Parameter ICUT
        # For spherical cuts
        #   =1 Standard polar cut with fixed phi
        #   =2 Conical cut with fixed theta
        # For planar and surface cut
        #   =1 Radial cut with fixed phi and variable distance rho
        #   =2 Circular cut at fixed rho and variable phi
        # For cylindrical cut
        #   =1 axial cut with fixed phi and variable z
        #   =2 circular cut with fixed z and variable phi
        self.icut = 1

        # Polarization definition for the cut
        # GRASP Parameter ICOMP
        # =1 Linear E_theta and E_phi.
        # =2 Right hand and left hand circular (Erhc and Elhc).
        # =3 Linear Eco and Ecx (Ludwig's third definition).
        # =4 Linear along major and minor axes of the polarisation ellipse, Emaj and Emin.
        # =5 XPD fields: E_theta/E_phi and E_phi/E_theta.
        # =6 XPD fields: Erhc/Elhc and Elhc/Erhc.
        # =7 XPD fields: Eco/Ecx and Ecx/Eco.
        # =8 XPD fields: Emaj/Emin and Emin/Emaj.
        # =9 Total power |E| and Erhc=Elhc.
        self.polarization = 3
        
        # Number of field components
        # GRASP Parameter NCOMP
        #   =2 for far field
        #   =3 for near field.  3rd component is always E_z
        self.field_components = 2
        
        # Cut Data
        self.data = []
        

    def read(self, lines):
        """Read cut from lines of text and parse as a cut, filing the
        parameters and data"""
        # Get the text descriptor and pop it off the front
        self.text = lines.pop(0)

        # Get the specification of the cut and parse it
        specline = lines.pop(0)
        specs = specline.split()
        self.v_ini = float(specs[0])
        self.v_inc = float(specs[1])
        self.v_num = int(specs[2])
        self.constant = float(specs[3])
        self.polarization = int(specs[4])
        self.icut = int(specs[5])
        self.field_components = int(specs[6])

        # Create the numpy structured array for the data
        if self.field_components == 3:
            self.data = numpy.zeros((self.v_num), dtype=([('pos','f4'),('f1','c8'),('f2','c8'),('f3','c8')]))
        else: # self.field_components == 2:
            self.data = numpy.zeros((self.v_num), dtype=([('pos','f4'),('f1','c8'),('f2','c8')]))
            
        # Parse lines
        for i in range(self.v_num):
            self.data[i]['pos'] = self.v_ini + self.v_inc*i
            l = lines[i].split()
            self.data[i]['f1'] = complex(float(l[0]), float(l[1]))
            self.data[i]['f2'] = complex(float(l[2]), float(l[3]))
            if self.field_components ==3:
                self.data[i]['f3'] = complex(float(l[4]), float(l[5]))
                

    def write(self):
        """Write local arrays to disk in GRASP cut file format"""
        pass
        
    def selectPosRange(self, pos_min, pos_max):
        """Returns a cut containing only the positions between pos_min
        and pos_max inclusive"""
        output = GRASP_cut()
        
        output.text = self.text
        output.cut_type = self.cut_type
        
        output.v_ini = pos_min
        output.v_inc = self.v_inc
        output.v_num = math.ceil((pos_max-pos_min)/self.v_inc)
        output.constant = self.constant
        output.polarization = self.polarization
        output.icut = self.icut
        output.field_components = self.field_components
        
        # Find the indices of points just within the pos_min and pos_max
        # limits
        i_min = 0
        i_max = self.data.shape[0]
        for d in range(self.data.shape[0]):
            if self.data[d]['pos'] >= pos_min:
                if i_min ==0:
                    i_min = d
            if self.data[d]['pos'] >= pos_max:
                if i_max>d:
                    i_max = d
                    
        # Set v_ini and v_num
        output.v_ini = self.data[i_min]['pos']
        output.v_num = i_max - i_min + 1
        
        # Set data
        output.data = self.data[i_min:i_max]

        return output
