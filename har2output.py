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
        DataFrame for imports (domestics (for regional) and external or just external)
    """
    def __init__(self, make, imports):
        self.VT = np.matrix(make)
        self.gt = self.VT.sum(axis=0)
        self.table = make
        self.table["Total_output"] = self.table.sum(axis = 1)  # colsum
        self.table = pd.concat([self.table, imports], axis=1)
        self.table["Total_supply"] = self.table["Total_output"] + imports.sum(axis = 1)
        self.q = self.table["Total_supply"].values
        self.table.loc["Products_total"] = self.table.sum() # rowsum

        
        

class regSupplyTables:
    """
    A class to hold a regional supply table

    Parameters
    ----------
    make_obj : HarFileObj
        A MAKE object from a har-file 
    trade_obj : HarFileObj
        A TRADE object for a har-file
    """
    def __init__(self, make_obj, trade_obj):
        
        def calc_imp(i, trade_obj):
            imp_dom = pd.DataFrame(np.delete(trade_obj["array"][:,0,:,i],i, axis = 1).sum(axis = 1), columns = ["Imports_domestic"], index=trade_obj["sets"][0]["dim_desc"])
            imp_ext = pd.DataFrame(trade_obj["array"][:,1,:,i].sum(axis = 1), columns = ["Imports_external"], index=trade_obj["sets"][0]["dim_desc"])
            imp = pd.concat([imp_dom, imp_ext], axis=1)
            return imp        

        self.ar = make_obj["array"]
        self.dims = {k["name"]: k["dim_desc"] for k in make_obj["sets"]}
        self.tables = {self.dims["DST"][i]: \
                       supplyTable(make = pd.DataFrame(self.ar[:,:,i], \
                                    columns = self.dims["IND"], index = self.dims["COM"]),\
                                   imports = calc_imp(i, trade_obj))\
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
    exp_dom: DataFrame
        A domestic export
    own_reg_share: array
        Share of use from own region in domestic use (COM x 1) 
    """
    def __init__(self, use, use_dom, va, exp_dom, own_reg_share):
        self.own_reg_share = own_reg_share
        self.dims = {"COM": use.index.tolist(), \
                    "IND": va.columns.tolist(),
                    "VA": va.index.tolist(),
                    "FINAL": use.columns[range(len(va.columns), len(use.columns))]}
        self.U = np.matrix(use[va.columns.tolist()])
        self.U_dom = np.matrix(use_dom[va.columns.tolist()])
        self.U_dom_own = np.multiply(self.U_dom, np.matrix(own_reg_share).transpose())
        self.Y_dom = np.matrix(use_dom[self.dims["FINAL"]])
        self.Y_dom_own = np.multiply(self.Y_dom, np.matrix(own_reg_share).transpose())
        self.Y_imp = np.matrix(use[self.dims["FINAL"]]) - np.matrix(use_dom[self.dims["FINAL"]])
        # Export matrix: domestic export, external export
        self.U_exp = np.concatenate([(self.U_dom - self.U_dom_own).sum(axis = 1), (self.U - self.U_dom).sum(axis = 1)], axis = 1).transpose()
        self.va = np.matrix(va)
        # self.table = use
        self.table_imp = pd.DataFrame(self.U_imp, index = ["Export internal", "Export external"], columns = self.dims["IND"])
        self.table = pd.concat([use, self.table_imp], axis=0)
        self.table = pd.concat([self.table, va], axis=0)
        # self.table = pd.concat([self.table, final], axis = 1)
        self.table = self.table.loc[use.index.tolist() + self.table_imp.index.tolist() + va.index.tolist(), use.columns.tolist()]   # to original order
        self.table["Total_supply"] = self.table.sum(axis = 1)


class regUseTables:
    """
    A class to hold a regional supply table

    Parameters
    ----------
    use_obj : HarFileObj
        A USE object from a har-file
    trade_obj : HarFileObj
        object from a har-file
    tradmar_obj : HarFileObj
        object from a har-file
    suppmar_obj : HarFileObj
        object from a har-file
    va_labour_obj : HarFileObj
        object from a har-file
    va_capital_obj : HarFileObj
        object from a har-file
    va_land_obj : HarFileObj
        object from a har-file


    """

    def __init__(self, use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj):
        # self.use_pp = use_obj["array"][:,0,0:len(va_labour_obj["sets"][0]["dim_desc"]),:]
        # self.final_pp = use_obj["array"][:,0,len(va_labour_obj["sets"][0]["dim_desc"]):,:]
        self.dims = {k["name"]: k["dim_desc"] for k in use_obj["sets"]}
        self.dims.update({"IND": va_labour_obj["sets"][0]["dim_desc"]})
        # self.va_labour = pd.DataFrame(va_labour_obj["array"].sum(axis = 1),
                                        #  index = self.dims["USR"][0:len(self.dims["COM"])])
        
        def calc_use_bp(i, use_obj, trade_obj, tradmar_obj, suppmar_obj):
            # Use at delivered prices (including margins)
            use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            suppmar = pd.DataFrame(suppmar_obj["array"][:,:,:,i].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"]) 
            tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"]) 
            margin = pd.DataFrame(pd.concat([tradmar, suppmar], axis=1)).fillna(0) 
            margin["Margins"] = margin["Trade_margin"] - margin["Suppy_margin"] 
            # Use at basic prices
            use_bp = use_dp - use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Margins"], axis = "rows") 
            return use_bp

        def calc_use_bp_dom(i, use_obj, trade_obj, tradmar_obj, suppmar_obj):
            # Use at delivered prices (including margins)
            use_dp = pd.DataFrame(use_obj["array"][:,0,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            suppmar = pd.DataFrame(suppmar_obj["array"][:,:,:,i].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"]) 
            tradmar = pd.DataFrame(tradmar_obj["array"][:,0,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"]) 
            margin = pd.DataFrame(pd.concat([tradmar, suppmar], axis=1)).fillna(0) 
            margin["Margins"] = margin["Trade_margin"] - margin["Suppy_margin"] 
            # Use at basic prices
            use_bp = use_dp - use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Margins"], axis = "rows") 
            return use_bp
                              
        self.tables = {self.dims["DST"][i]: \
                        useTable(use = calc_use_bp(i, use_obj, trade_obj, tradmar_obj, suppmar_obj),\
                                # final =  pd.DataFrame(self.final[:,:,i], \
                                    # columns = self.dims["USR"][len(self.use[:,1,i]):], index = self.dims["COM"]),\
                                va = pd.DataFrame(\
                                    {va_labour_obj["coeff_name"].strip(): va_labour_obj["array"].sum(axis = 1)[:,i],\
                                     va_capital_obj["coeff_name"].strip(): va_capital_obj["array"][:,i],\
                                     va_land_obj["coeff_name"].strip(): va_land_obj["array"][:,i]},\
                                     index=self.dims["IND"]).transpose(),\
                                use_dom = calc_use_bp_dom(i, use_obj, trade_obj, tradmar_obj, suppmar_obj), \
                                # Domestic export: flow from i to all other than i
                                exp_dom = pd.DataFrame(np.delete(trade_obj["array"][:,0,i,:], i, axis=1).sum(axis = 1), index=self.dims["COM"], columns = ["Domestic_export"]), \
                                # Share of own region is use: flow from i to i / flow from all to i
                                own_reg_share = (trade_obj["array"][:,0,i,i] / trade_obj["array"][:,0,:,i].sum(axis = 1))) \
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

def build_io(sup_tab, use_tab):
    """ 
    To build input-output table from supply and use tables
    """
    # B = T * U = V * inv(diag(q)) * U
    B = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.U_dom
    # F = T * Y = V * inv(diag(q)) * Y
    F = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Y_dom
    W = use_tab.va  
    B = pd.DataFrame(B, index=use_tab.dims["COM"], columns=use_tab.dims["IND"])
    F = pd.DataFrame(F, index=use_tab.dims["COM"], columns=use_tab.dims["FINAL"])
    W = pd.DataFrame(W, index=use_tab.dims["VA"], columns=use_tab.dims["IND"])
    return ioTable(B, F, W)  


# reg_supp.tables["Uusimaa"].VT.shape

