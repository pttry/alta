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
    own_reg_share: array
        Share of use from own region in domestic use (COM x 1) 
    """
    def __init__(self, use, use_dom, va, own_reg_share):
        self.own_reg_share = own_reg_share
        self.dims = {"COM": use.index.tolist(), \
                    "IND": va.columns.tolist(),
                    "VA": va.index.tolist(),
                    "FINAL": use.columns[range(len(va.columns), len(use.columns))]}
        # Matrices
        self.U = np.matrix(use[self.dims["IND"]])
        self.Ud = np.matrix(use_dom[self.dims["IND"]])
        self.Ur = np.multiply(self.Ud, np.matrix(own_reg_share).transpose())
        self.Umdom = self.Ud - self.Ur
        self.Umext = self.U - self.Ud

        self.Y = np.matrix(use[self.dims["FINAL"]])
        self.Yd = np.matrix(use_dom[self.dims["FINAL"]])
        self.Yr = np.multiply(self.Yd, np.matrix(own_reg_share).transpose()) 
        self.Ymdom = self.Yd - self.Yr
        self.Ymext = self.Y - self.Yd
        
        self.W = np.matrix(va)

        # tables 

        self.table = pd.DataFrame(self.U, index = self.dims["COM"], columns = self.dims["IND"])
        self.table["Sum"] = self.table.sum(axis = 1)
        table_int = self.table
        self.table = pd.concat([self.table, pd.DataFrame(self.Y, index = self.dims["COM"], columns = self.dims["FINAL"])], axis=1)
        self.table.loc["Product_use"] = self.table.sum(axis = 0)
        self.table["Total_use"] = self.table[self.dims["FINAL"]].sum(axis = 1).add(self.table["Sum"]) 
        table_va = pd.DataFrame(self.W, index = self.dims["VA"], columns = self.dims["IND"])
        table_va["Sum"] = table_va.sum(axis = 1)
        self.table = pd.concat([self.table, table_va], axis=0)[self.table.columns.tolist()]
        self.table.loc["Output"] = table_int.sum(axis = 0) + table_va.sum(axis = 0)
              

        # # Total
        # self.U = np.matrix(use[va.columns.tolist()])
        # self.va = np.matrix(va)
        # self.Y = np.matrix(use[self.dims["FINAL"]])
        # self.table = pd.concat([use, self.table_imp], axis=0)
        # self.table = pd.concat([self.table, va], axis=0)
        # # self.table = pd.concat([self.table, final], axis = 1)
        # self.table = self.table.loc[use.index.tolist() + self.table_imp.index.tolist() + va.index.tolist(), use.columns.tolist()]   # to original order
        # self.table["Total_supply"] = self.table.sum(axis = 1)

        # # Domestic total
        # self.U_dom = np.matrix(use_dom[va.columns.tolist()])
        # # Domestic import

        # # External import
        # self.U_imp_ext = self.U - self.U.dom
        # self.U_dom_own = np.multiply(self.U_dom, np.matrix(own_reg_share).transpose())
        # self.Y_dom = np.matrix(use_dom[self.dims["FINAL"]])
        # self.Y_dom_own = np.multiply(self.Y_dom, np.matrix(own_reg_share).transpose())
        # self.Y_imp = np.matrix(use[self.dims["FINAL"]]) - np.matrix(use_dom[self.dims["FINAL"]])
        # # Export matrix: domestic export, external export
        # self.U_exp = np.concatenate([(self.U_dom - self.U_dom_own).sum(axis = 1), (self.U - self.U_dom).sum(axis = 1)], axis = 1).transpose()
        
        # # self.table = use
        # self.table_imp = pd.DataFrame(self.U_imp, index = ["Export internal", "Export external"], columns = self.dims["IND"])



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
    prodtaxes_obj : HarFileObj
        object from a har-file


    """

    def __init__(self, use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj):
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
             # Domestic export: flow from i to all other than i
            exp_dom = np.delete(trade_obj["array"][:,0,i,:], i, axis=1).sum(axis = 1)
            use_bp["Exp_dom"] = exp_dom
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
             # Domestic export: flow from i to all other than i
            exp_dom = np.delete(trade_obj["array"][:,0,i,:], i, axis=1).sum(axis = 1)
            use_bp["Exp_dom"] = exp_dom
            return use_bp
                              
        self.tables = {self.dims["DST"][i]: \
                        useTable(use = calc_use_bp(i, use_obj, trade_obj, tradmar_obj, suppmar_obj),\
                                # final =  pd.DataFrame(self.final[:,:,i], \
                                    # columns = self.dims["USR"][len(self.use[:,1,i]):], index = self.dims["COM"]),\
                                va = pd.DataFrame(\
                                    {va_labour_obj["coeff_name"].strip(): va_labour_obj["array"].sum(axis = 1)[:,i],\
                                     va_capital_obj["coeff_name"].strip(): va_capital_obj["array"][:,i],\
                                     va_land_obj["coeff_name"].strip(): va_land_obj["array"][:,i],\
                                     prodtaxes_obj["coeff_name"].strip(): prodtaxes_obj["array"][:,i]},\
                                     index=self.dims["IND"]).transpose(),\
                                use_dom = calc_use_bp_dom(i, use_obj, trade_obj, tradmar_obj, suppmar_obj), \
                                # Share of own region is use: flow from i to i / flow from all to i
                                own_reg_share = (trade_obj["array"][:,0,i,i] / trade_obj["array"][:,0,:,i].sum(axis = 1))) \
                        for i in range(len(self.dims["DST"]))}

    def to_excel(self, file):
        writer = pd.ExcelWriter(file, engine='xlsxwriter')
        for key,values in self.tables.items():
                values.table.to_excel(writer, sheet_name = key)
        writer.save()


class IOTable:
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

class regIOtables:
    """
    A class to hold an regional input-ouput tables

    Parameters
    ----------
    sup : Obj
        Object from regSupplyTables
    use : Obj
        Object from regUseTables   

    """

    def __init__(self, sup, use):

        def build_io(sup_tab, use_tab):
            """ 
            To build input-output table from supply and use tables
            """
            # B = T * U = V * inv(diag(q)) * U
            Br = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Ur
            Bmdom = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Umdom
            Bmext = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Umext
            # F = T * Y = V * inv(diag(q)) * Y
            Fr = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Yr
            Fmdom = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Ymdom
            Fmext = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Ymext
            W = use_tab.W  

            B = pd.DataFrame(Br, index=use_tab.dims["COM"], columns=use_tab.dims["IND"])
            B.loc["Domestic_import"] = pd.DataFrame(Bmdom, columns=use_tab.dims["IND"]).sum(axis = 0)
            B.loc["External_import"] = pd.DataFrame(Bmext, columns=use_tab.dims["IND"]).sum(axis = 0)

            F = pd.DataFrame(Fr, index=use_tab.dims["COM"], columns=use_tab.dims["FINAL"])
            F.loc["Domestic_import"] = pd.DataFrame(Fmdom, columns=use_tab.dims["FINAL"]).sum(axis = 0)
            F.loc["External_import"] = pd.DataFrame(Fmext, columns=use_tab.dims["FINAL"]).sum(axis = 0)
            
            W = pd.DataFrame(W, index=use_tab.dims["VA"], columns=use_tab.dims["IND"])
            return ioTable(B, F, W)  

        self.tables = {i : build_io(sup.tables[i], use.tables[i]) \
                        for i in sup.tables.keys()}

    def to_excel(self, file):
        writer = pd.ExcelWriter(file, engine='xlsxwriter')
        for key,values in self.tables.items():
                values.table.to_excel(writer, sheet_name = key)
        writer.save()




