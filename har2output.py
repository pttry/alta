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



class useTable:
    """
    A class to hold a use table

    Parameters
    ----------
    use : Datarame
        DataFrame for a use matrix 
    final : DataFrame
        DataFrame for a final use matrix
    va : DataFrame
        DataFrame for a value added matrix
        labour 1LAB
        capital 1CAP
        land 1LND
        taxes on production 1PTX
    """
    def __init__(self, use, final, va):
        self.use = np.matrix(use)
        self.final = np.matrix(final)
        self.va = np.matrix(va)
        self.table = use
        self.table = pd.concat([use, va])
        self.table = pd.concat([self.table, final], axis = 1)
        self.table = self.table.loc[use.index.tolist() + final.index.tolist(), use.columns.tolist() + va.columns.tolist()]   # to original order


class regUseTables:
    """
    A class to hold a regional supply table

    Parameters
    ----------
    use_obj : HarFileObj
        A USE object for a har-file
    """
    def __init__(self, use_obj, va_labour_obj, va_capital_obj, va_land_obj):
        self.use = use_obj["array"][:,0,0:len(va_labour_obj["sets"][0]["dim_desc"]),:]
        self.final = use_obj["array"][:,0,len(va_labour_obj["sets"][0]["dim_desc"]):,:]
        self.dims = {k["name"]: k["dim_desc"] for k in use_obj["sets"]}
        self.dims.update({"IND": va_labour_obj["sets"][0]["dim_desc"]})
        self.va_labour = pd.DataFrame(va_labour_obj["array"].sum(axis = 1),
                                         index = self.dims["USR"][0:len(self.dims["COM"])])
        self.tables = {self.dims["DST"][i]: \
                       useTable(use = pd.DataFrame(self.use[:,:,i], \
                                    columns = self.dims["IND"], index = self.dims["COM"]),\
                                final =  pd.DataFrame(self.final[:,:,i], \
                                    columns = self.dims["USR"][len(self.use[:,1,i]):], index = self.dims["COM"]),\
                                va = pd.DataFrame(\
                                    {va_labour_obj["coeff_name"].strip(): va_labour_obj["array"].sum(axis = 1)[:,i],\
                                     va_capital_obj["coeff_name"].strip(): va_capital_obj["array"][:,i],\
                                     va_land_obj["coeff_name"].strip(): va_land_obj["array"][:,i]},\
                                     index=self.dims["IND"]).transpose())\
                        for i in range(len(self.dims["DST"]))}

    def to_excel(self, file):
        writer = pd.ExcelWriter(file, engine='xlsxwriter')
        for key,values in self.tables.items():
                values.table.to_excel(writer, sheet_name = key)
        writer.save()


class ioTable:
    """
    A class to hold an input-ouput  table

    Parameters
    ----------
    B : Datarame
        DataFrame for a intermediates matrix 
    F : DataFrame
        DataFrame for a final use matrix
    W : DataFrame
        DataFrame for a value added matrix

    """
    def __init__(self, B, F, W):
        self.B = np.matrix(B)
        self.F = np.matrix(F)
        self.W = np.matrix(W)
        self.table = B
        self.table = pd.concat([B, W])
        self.table = pd.concat([self.table, F], axis = 1)
        self.table = self.table.loc[B.index.tolist() + W.index.tolist(), B.columns.tolist() + F.columns.tolist()]   # to original order

