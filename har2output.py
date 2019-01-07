# -*- coding: utf-8 -*-
"""
Trasforming HAR file objects of output ready

@author: jh
"""

# Basic modules
import pandas as pd
import numpy  as np
import os

import harpy

class supplyTable:
    """
    A class to hold a supply table

    Parameters
    ----------
    make : DataFrame
        DataFrame for a make matrix 
    use_imp : Datarame
        DataFrame for a sum of import use , 1-column
    """
    def __init__(self, make, use_imp):
        self.VT = np.matrix(make)
        self.q = self.VT.sum(axis=1)
        self.gt = self.VT.sum(axis=0)
        self.table = make
        self.table["Total_output"] = self.table.sum(axis=1)  # colsum
        self.table["Imports"] = use_imp.values
        self.table.loc["Products_total"] = self.table.sum() # rowsum
        self.table["Total_supply"] = self.table["Total_output"] + self.table["Imports"]

class regSupplyTables:
    """
    A class to hold a regional supply table

    Parameters
    ----------
    make_obj : HarFileObj
        A MAKE object from a har-file 
    use_obj : HarFileObj
        A USE object for a har-file
    """
    def __init__(self, make_obj, use_obj):
        self.ar = make_obj["array"]
        self.dims = {k["name"]: k["dim_desc"] for k in make_obj["sets"]}
        self.imp = pd.DataFrame(use_obj["array"][:,1,:,:].sum(axis = 1))
        self.tables = {self.dims["DST"][i]: \
                       supplyTable(make = pd.DataFrame(self.ar[:,:,i], \
                                    columns = self.dims["IND"], index = self.dims["COM"]),\
                                   use_imp = self.imp[[i]])\
                        for i in range(len(self.dims["DST"]))}

    def to_excel(self, file):
        writer = pd.ExcelWriter(file, engine='xlsxwriter')
        for key,values in self.tables.items():
                values.table.to_excel(writer, sheet_name = key)
        writer.save()



class useTableDom:
    """
    A class to hold a use table

    Parameters
    ----------
    use_dom : Datarame
        DataFrame for a domestic use matrix including final use
    labour 1LAB
    capital 1CAP
    land 1LND
    taxes on production 1PTX
    """
    def __init__(self, use_dom):
        self
