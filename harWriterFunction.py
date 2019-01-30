# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 15:45:03 2018

@author: jl, jh
"""
import numpy as np
import os
import subprocess
from harpy.har_file import HarFileObj
from harpy.header_array import HeaderArrayObj as HAO


def data2har(data, allDims):
    """
    Writes data from pandas to ViewHar format (GEMPACK data format).
    Requires harpy module to be installed. See 
    https://github.com/GEMPACKsoftware/HARPY for info.
    
    Input format:
    A dictionary, where key is the coefficient name.
    Dict value is a tuple, containing following data in the following order:
    DATA:
    1. data to write (can be a single parameter, pd.DataFrame, pd.Series..)
    2. header name
    3. long name to explain data content
    4. a list containing the dimensions of the data
    
    allDims:
    the dimensions that appear in the input data must be given as a separate
    dictionary as follows:
    key: dimension name
    value: list of dimension values.
    
    e.g
    allDims = {"COM": ["COM1", "COM2", "COM3"]}
    """
    HARfiles = HarFileObj()
    
    for key in data:
        # If it is a list of SETS:
        if type(data[key]) == list:
            newHead = HAO.HeaderArrayFromData(name=key,
                       array = np.array(data[key]))
            HARfiles.addHeaderArrayObj(newHead)
            
        else:
        # If it is a tuple with numeric data:
            array = data[key][0]
            name  = data[key][1]
            long_name  = data[key][2]
            dimensions = data[key][3]
            coeff_name = key

            if type(array) == float or type(array) == int or type(array) == np.float64:
                array = np.array(array, dtype=np.float32)
            if type(array) == np.ndarray:
                array = array.astype(np.float32)
            else:
                array = np.array(array.values, dtype = np.float32)

            sets = []

            if not dimensions:
                pass
            else:
                for dim in dimensions:
                    if dim not in allDims.keys():
                        raise ValueError("Dimension", dim, "not specified! Check the dimension dictionary.") 
                        
                    else:
                        setDict = {}
                        setDict["name"] = dim
                        setDict["dim_desc"] = allDims[dim]
                        setDict["dim_type"] = "Set"                    
                    
         
                        sets.append(setDict)       

            newHead = HAO.HeaderArrayFromData(name = name,  
                                                   array = array, 
                                                   coeff_name = coeff_name,
                                                   long_name = long_name,  
                                                   sets = sets)

            HARfiles.addHeaderArrayObj(newHead)
        
    return HARfiles


def aggHAR(har_dir, old, new, sup):
    """
    Aggregate HAR-file with agghar executable.
    The agghar is part of BUNDLE16 available from:
    http://www.copsmodels.com/gpmark9.htm

    Parameters
    ----------
    har_dir : str
        Folder of HAR-files
    old : str
        Original HAR-file 
    new : str
        HAR-file for aggregate values
    sup : str
        A mapping HAR-file 

    """
    try:
        os.remove(os.path.join(har_dir, new)) 
    except OSError:
        pass
    
    p = subprocess.Popen(["agghar", old, new, sup], cwd=har_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    if p.returncode != 0:
        print(out)
    else:
        print("OK")

def mergeHAR(har_dir, har1, har2, new):
    """
    Combine har1 (basedata30) and har2 (regExtension) into a single file new (basedata)
    with mergehar executable.
    The mergehar.exe is part of BUNDLE16 available from:
    http://www.copsmodels.com/gpmark9.htm


    Parameters
    ----------
    har_dir : str
        Folder of HAR-files
    har1 : str
        A first HAR-file 
    har2 : str
        a second HAR-file
    new : str
        A merged HAR-file 

    """
    try:
        os.remove(os.path.join(har_dir, new)) 
    except OSError:
        pass
    
    p = subprocess.Popen(["mergehar", har1, har2, new, "YY1"], cwd=har_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    if p.returncode != 0:
        print(out)
    else:
        print("OK")


def govgeneric():
    """
    Run govgeneric2.bat
    bat is as govgeneric.bat, but without a pause

    Parameters
    ----------


    """
    
    p = subprocess.Popen(["govgeneric2.bat"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    if p.returncode != 0:
        print(out)
    else:
        print("OK")

def mkdata2():
    """
    Run mkdata2.bat
    bat is as mkdata.bat, but without a pause

    Parameters
    ----------


    """
    
    p = subprocess.Popen(["mkdata2.bat"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    if p.returncode != 0:
        print(out)
    else:
        print("OK")
