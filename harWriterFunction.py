# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 15:45:03 2018

@author: jlehtomaa
"""
import numpy as np
from harpy.har_file import HarFileObj
from harpy.header_array import HeaderArrayObj as HAO


def data2har(data, allDims):
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