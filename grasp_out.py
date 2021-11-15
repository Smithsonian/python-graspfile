import numpy as np

def extract_spillover(fname):
    """Takes a filename of an .out file and searches it for the "Relative Power hitting reflector" values, calculates the "spillover" value given in the line below and returns a dictionary with the PO-value pairs"""
    spill_dict={}
    names_PO=[]
    values_spill=[]
    f=open(fname,"r")
    for num,line in enumerate(f.readlines()):
        if "get_currents" in line:
            name=line.split()[0]
            names_PO.append(name)
        if "Relative power" in line:
            value=float(line.split()[4])
            values_spill.append([value,-10*np.log10(value)])
    for i in range(len(names_PO)):
        spill_dict[names_PO[i]]=values_spill[i]
    return spill_dict