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
        DataFrame for make matrix 
    """
    def __init__(self, make):
        self.VT = np.matrix(make)
        self.q = self.VT.sum(axis=1)
        self.gt = self.VT.sum(axis=0)
        self.table = make
        self.table["Total_output"] = self.table.sum(axis=1)  # colsum
        self.table.loc["Products_total"] = self.table.sum() # rowsum

class regSupplyTables:
    """
    A class to hold a regional supply table

    Parameters
    ----------
    har_obj : HarFileObj
        A HAR-file object from har file 
    """
    def __init__(self, har_obj):
        self.ar = har_obj["array"]
        self.dims = {k["name"]: k["dim_desc"] for k in har_obj["sets"]}
        self.tables = {self.dims["DST"][i]: \
                       supplyTable(pd.DataFrame(self.ar[:,:,i], \
                                    columns = self.dims["IND"], index = self.dims["COM"]))\
                        for i in range(len(self.dims["DST"]))}

    def to_excel(self, file):
        writer = pd.ExcelWriter(file, engine='xlsxwriter')
        for key,values in self.tables.items():
                values.table.to_excel(writer, sheet_name = key)
        writer.save()




