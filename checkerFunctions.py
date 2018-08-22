# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 15:29:49 2018
@author: jl
"""

# Procedures to quickly check that data are balanced, contain no unwanted
# negative values or NaN values.
import numpy as np

def checkColSums(a, b, allowDifference):
    """
    Check that all elements in column sums of two dataframes are within 
    allowed error margin.
    a,b = pd.DataFrames
    allowDifference = max difference, e.g. 0.05
    """
    if len(a.index) != len(b.index):
        raise ValueError("Dataframes lengths do not match!")
    
    diff = a.sum(axis=1) - b.sum(axis=1)
    if all(abs(diff < allowDifference)):
        print("OK!")
    else:
        print("ERRORS FOUND IN\n", diff[diff>allowDifference])
                
        
def checkCols(a, b, allowDifference):
    """
    Check that all elements in two series are within 
    allowed error margin.
    a,b = pd.Series
    allowDifference = max difference, e.g. 0.05
    """
    if len(a.index) != len(b.index):
        raise ValueError("Series lengths do not match!")
    diff = a - b
    if all(diff < allowDifference):
        print("OK!")
    else:
        print("ERRORS IN", diff[diff>allowDifference])     
        
def checkNums(a,b, allowDifference):
    """
    Check that two values (integers or floats) are within a specified error
    margin.
    """
    diff = float(a) - float(b)
    if abs(diff) < allowDifference:
        print("OK!")
    else:
        print("ERRORS IN", diff[diff>allowDifference])
        
def check4negs(dataframe):
    """
    Input: a pandas dataframe.
    Checks if the df contains negative values.
    """
    negValues = []
    for row in dataframe.index:
        for column in dataframe:
            value = dataframe.loc[row][column]
            if value <0:
                negValues.append((row, column, value))
    if not negValues:
        print("No negative values")
    else:
        print("Negative values in", negValues)
    
def check4nans(dataframe):
    """
    Input: a pandas dataframe.
    Checks if the df containsi any NaN values.
    """
    nanValues = []
    for row in dataframe.index:
        for column in dataframe:
            value = dataframe.loc[row][column]
            if np.isnan(value):
                nanValues.append((row, column, value))
    if not nanValues:
        print("No nan values")
    else:
        print("Nan values in", nanValues)
        
