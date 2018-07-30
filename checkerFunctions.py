# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 15:29:49 2018

@author: jlehtomaa
"""
import numpy as np
# Define checker functions:
def checkColSums(a, b, allowDifference):
    diff = a.sum(axis=1) - b.sum(axis=1)
    if all(abs(diff < allowDifference)):
        print("OK!")
    else:
        print("ERRORS FOUND IN\n", diff[diff>allowDifference])
                
def checkCols(a, b, allowDifference):
    diff = a - b
    if all(diff < allowDifference):
        print("OK!")
    else:
        print("ERRORS IN", diff[diff>allowDifference])     
        
def checkNums(a,b, allowDifference):
    diff = float(a) - float(b)
    if abs(diff) < allowDifference:
        print("OK!")
    else:
        print("ERRORS IN", diff[diff>allowDifference])
        
def check4negs(dataframe, printOK = True):
    negValues = []
    for row in dataframe.index:
        for column in dataframe:
            value = dataframe.loc[row][column]
            if value <0:
                negValues.append((row, column, value))
    if not negValues:
        if printOK:
            print("No negative values")
        if not printOK:
            pass
    else:
        return negValues
    
    
def check4nans(dataframe, printOK = True):
    nanValues = []
    for row in dataframe.index:
        for column in dataframe:
            value = dataframe.loc[row][column]
            if np.isnan(value):
                nanValues.append((row, column, value))
    if not nanValues:
        if printOK:
            print("No nan values")
        if not printOK:
            pass
    else:
        return nanValues
