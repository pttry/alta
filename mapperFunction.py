# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 13:08:16 2018

@author: jllg
"""

def mapperFunction(longData, shortData, exceptions = {}, orderNum = False):
    """
    This function takes in two lists, a long one and a short one, and creates
    a mapping between the datasets. List entries (industries or commodities) must
    be in the FINAGE format, that is, in the form prefix_code.
    
    This function returns a dictionary, where the original long data is stored in keys, 
    and the aggregated set is stored in values.
    E.g. "I_23534" and "I_24564" might be stored under an aggregate set "I_23_24".
    """
    result = {}
    targetRanges = dict(zip([x for x in shortData if "_" in x[2:]],
           [range(int(a.split("_")[0]), int(a.split("_")[1])+1) for a in [x[2:] for x in shortData if "_" in x[2:]]] ))
    
    for x in longData:
        mapHere = "NAN" # A flag for mapping errors
        dataCode = x[0:4]
        
        # If included in a list of exceptions:
        if x in [val for key in sorted(exceptions) for val in exceptions[key]]:
            for k,v in exceptions.items():
                if x in v:
                    mapHere = k
                    if orderNum:
                        mapHere = shortData.index(k)+1
                        
        # If a direct match between long and short data                   
        elif x in shortData:
            mapHere = x
            if orderNum:
                mapHere = shortData.index(x)+1
                
        # If the truncated datacode from longdata matches shortdata (e.g. I_0111 is paired with I_01)            
        elif dataCode in shortData:
            mapHere = dataCode
            if orderNum:
                mapHere = shortData.index(dataCode)+1
                
        # If the long datacode falls within the range of values in the short data
        elif any(int(dataCode[2:]) in v for k,v in targetRanges.items()):
            matchingRange = next((k for k, v in targetRanges.items() if int(dataCode[2:]) in v), None)
            mapHere = matchingRange
            if orderNum:
                mapHere = shortData.index(matchingRange)+1
        
        if orderNum:
            result[longData.index(x)+1] = mapHere
        else:  
            result[x] = mapHere 
    
    if any("NAN" in v for v in result.values()):
        raise ValueError("SOME ENTRIES IN LONG DATA WERE NOT MAPPED!")
    if not all(a in result.values() for a in shortData):
        raise ValueError("SOME ENTRIES IN SHORT DATA FOUND NO MATCH IN LONG DATA!")  
    if len(result) != len(longData):
        raise ValueError("SOME ENTRIES FROM LONG DATA NOT FOUND IN THE AGGREGATION KEY!")
        
    return result