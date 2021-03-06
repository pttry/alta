# -*- coding: utf-8 -*-
"""
Trasforming HAR file objects of output ready

@author: jh
"""

# Basic modules
import pandas as pd
import numpy  as np
import os
import copy

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
    def __init__(self, make, imports, stocks):
        self.dims = {"COM": make.index.tolist(), \
                    "IND": make.columns.tolist()}
        s=pd.DataFrame(stocks) 
        stocks=s.transpose() 
        stocks.index=["Stocks"] 
        stocks.columns=self.dims["IND"]
        make2 = pd.DataFrame(make, columns = self.dims["IND"], index = self.dims["COM"])
        make3 = make2 + make2.div(make2.sum(axis=0), axis = "columns").mul(stocks.loc["Stocks"], axis = "columns")
        self.M=make3
        self.Inv=make3.sum(axis=1)
        self.VT = np.matrix(make3)
        self.gt = self.VT.sum(axis=0)
        self.table = make3
        self.table["I_0"] = self.table.sum(axis = 1)  # colsum
        self.table = pd.concat([self.table, imports], axis=1, sort=True)
        self.table["SUPP"] = self.table["I_0"] + imports.sum(axis = 1)
        self.q2 = self.table["SUPP"].values
        self.q = self.table["I_0"].values
        self.table.loc["Prod_total"] = self.table.sum() # rowsum

        
        

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
    def __init__(self, make_obj, use_obj, tradmar_obj, suppmar_obj, trade_obj, stocks_obj):
        
        def calc_imp(i, use_obj, trade_obj, tradmar_obj, suppmar_obj,make_obj, stocks_obj):
            use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
            tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = pd.DataFrame(tradmar).fillna(0)
            margin["Sup_pr"]=suppmar.div(suppmar.sum(axis=0)).fillna(0)
            margin = margin.fillna(0)
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows")
            use_dp_sp_45_47=(use_dp_tr*suppmar_obj["array"][0,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_dp_sp_49_53=(use_dp_tr*suppmar_obj["array"][1,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_bp = use_dp - use_dp_tr
            use_bp.loc["C_45_47"]=use_dp.loc["C_45_47"]+use_dp_sp_45_47
            use_bp.loc["C_49_53"]=use_dp.loc["C_49_53"]+use_dp_sp_49_53
            #spread imports
            use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = margin.fillna(0)
            # Use at basic prices
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
            use_bp_i = use_dp - use_dp_tr
            #total domestic after margins (dom+regions)
            use_bp=use_bp-use_bp_i
            use_bp_exp=use_bp["Exp"]  
            #dom        
            own_reg_share = (trade_obj["array"][:,0,i,i] / trade_obj["array"][:,0,:,i].sum(axis = 1)) 
            u = np.matrix(use_bp)
            use_bp= np.multiply(u, np.matrix(own_reg_share).transpose())
            use_bp= pd.DataFrame(use_bp, columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            #use_bp["Exp"] = use_bp_exp
            #use_bp["Exp"] = use_bp_exp
            make2 = pd.DataFrame(make_obj["array"][:,:,i], columns = make_obj["sets"][1]["dim_desc"], index = make_obj["sets"][0]["dim_desc"])
            cor=make2.sum(axis=1)-use_bp.sum(axis=1)
            s_C_45_47=np.array(cor.loc["C_45_47"])
            s_C_49_53=np.array(cor.loc["C_49_53"])
            exp_dom=pd.DataFrame(np.delete(trade_obj["array"][:,0,i,:], i, axis=1).sum(axis = 1), columns=["EXP"], index=trade_obj["sets"][0]["dim_desc"])
            s1_C_45_47=np.array(exp_dom.loc["C_45_47"]+np.delete(suppmar_obj["array"][0,:,:,i], i, axis=1).sum())-s_C_45_47
            s1_C_49_53=np.array(exp_dom.loc["C_49_53"]+np.delete(suppmar_obj["array"][1,:,:,i], i, axis=1).sum())-s_C_49_53


            imp_dom = pd.DataFrame(np.delete(trade_obj["array"][:,0,:,i],i, axis = 1).sum(axis = 1), columns = ["IMP_REG"], index=trade_obj["sets"][0]["dim_desc"])
            imp_ext = pd.DataFrame(use_obj["array"][:,1,:,i].sum(axis=1)-tradmar_obj["array"][:,1,:,:,i].sum(axis=(1,2)),columns = ["IMP_FOR"], index=trade_obj["sets"][0]["dim_desc"])
            imp_dom.loc["C_45_47"]=imp_dom.loc["C_45_47"]+np.delete(suppmar_obj["array"][0,:,i,:], i, axis=1).sum()-s1_C_45_47
            imp_dom.loc["C_49_53"]=imp_dom.loc["C_49_53"]+np.delete(suppmar_obj["array"][1,:,i,:], i, axis=1).sum()-s1_C_49_53
            imp = pd.concat([imp_dom, imp_ext], axis=1, sort=True)

            return imp        

        self.ar = make_obj["array"]
        self.dims = {k["name"]: k["dim_desc"] for k in make_obj["sets"]}
        self.tables = {self.dims["DST"][i]: \
            supplyTable(make=pd.DataFrame(self.ar[:,:,i], columns = self.dims["IND"], index = self.dims["COM"]) , \
                imports = calc_imp(i, use_obj, trade_obj, tradmar_obj, suppmar_obj,make_obj, stocks_obj) ,\
                stocks=stocks_obj["array"][:,i])

    for i in range(len(self.dims["DST"]))}

    def to_excel(self, file):
        writer = pd.ExcelWriter(file, engine='xlsxwriter')
        for key,values in self.tables.items():
                values.table.to_excel(writer, sheet_name = key)
                workbook  = writer.book
                worksheet = writer.sheets[key]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                format.set_num_format('0.000')
                format.set_text_wrap()
                worksheet.set_column(0,41,15, format)
                
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
    def __init__(self, use_dom, use_reg, use_imp, va, tax_f):
        self.dims = {"COM": use_dom.index.tolist(), \
                    "IND": va.columns.tolist(),
                    "VA": va.index.tolist(),
                    "FINAL": use_dom.columns[range(len(va.columns), len(use_dom.columns))]}
        # Matrices
        self.U = np.matrix(use_dom[self.dims["IND"]])+np.matrix(use_reg[self.dims["IND"]])+np.matrix(use_imp[self.dims["IND"]])
        self.Ud = np.matrix(use_dom[self.dims["IND"]])
        self.Umdom = np.matrix(use_reg[self.dims["IND"]])
        self.Umext = np.matrix(use_imp[self.dims["IND"]])

        self.Y = np.matrix(use_dom[self.dims["FINAL"]])+np.matrix(use_reg[self.dims["FINAL"]])+np.matrix(use_imp[self.dims["FINAL"]])
        self.Yd = np.matrix(use_dom[self.dims["FINAL"]])
        self.Ymdom = np.matrix(use_reg[self.dims["FINAL"]])
        self.Ymext = np.matrix(use_imp[self.dims["FINAL"]])

        self.W =  np.matrix(va)
        self.tax_f=tax_f
        W=pd.DataFrame(self.W, index = self.dims["VA"], columns = self.dims["IND"])
        tax_f=pd.DataFrame(np.matrix(tax_f))
        
               # tables 
        U=pd.DataFrame(self.U, index=self.dims["COM"], columns=self.dims["IND"])
        U.loc["Prod_total"]=U.sum(axis=0)
        self.table = pd.DataFrame(U, index=self.dims["COM"] +["Prod_total"])
        self.table.loc["TAX_SUB"]=W.loc["TAXES"]
        K=pd.DataFrame(self.table, columns = self.dims["IND"]) 
        self.table.loc["TOT_INT"]=K.sum(axis=0)-self.table.loc["Prod_total"]
        self.table.loc["V1LAB"]=W.loc["V1LAB"]
        self.table.loc["V1CAP"]=W.loc["V1CAP"]
        self.table.loc["V1LND"]=W.loc["V1LND"]
        self.table.loc["V1PTX"]=W.loc["V1PTX"]
        self.table.loc["VA"]=W.loc["V1LAB"] + W.loc["V1CAP"] + W.loc["V1LND"]+W.loc["V1PTX"]
        self.table.loc["P1R"] = self.table.loc["TOT_INT"]+self.table.loc["VA"]
        self.table["IND_TOT"] = self.table.sum(axis = 1)
        Y=pd.DataFrame(self.Y, index=self.dims["COM"], columns=self.dims["FINAL"])
        Y.loc["Prod_total"]=Y.sum(axis=0)
        tax_f["EXP_REG"]=0
        tax_f["Inventories"]=0
        tax_f=pd.DataFrame(np.matrix(tax_f), index=["TAX_SUB"], columns= self.dims["FINAL"])
        Y=pd.concat([Y, tax_f], axis=0)
        Y.loc["TOT_INT"]=Y.loc["TAX_SUB"]+Y.loc["Prod_total"]
        self.table = pd.concat([self.table, pd.DataFrame(Y, index =self.dims["COM"] +["Prod_total", "TAX_SUB", "TOT_INT"], columns = self.dims["FINAL"])], axis=1, sort=False)
        K2=pd.DataFrame(self.table, index =self.dims["COM"] +["Prod_total", "TAX_SUB", "TOT_INT"], columns = self.dims["FINAL"] )
        self.table["FIN_USE"] = K2.sum(axis = 1)
        K2=pd.DataFrame(self.table, index =self.dims["COM"] +["Prod_total", "TAX_SUB", "TOT_INT"])
        self.table["TOT_USE"] = K2["FIN_USE"]+K2["IND_TOT"]
        
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

    def __init__(self, use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj, taxes_obj, make_obj, stocks_obj):
        # self.use_pp = use_obj["array"][:,0,0:len(va_labour_obj["sets"][0]["dim_desc"]),:]
        # self.final_pp = use_obj["array"][:,0,len(va_labour_obj["sets"][0]["dim_desc"]):,:]
        self.dims = {k["name"]: k["dim_desc"] for k in use_obj["sets"]}
        self.dims.update({"IND": va_labour_obj["sets"][0]["dim_desc"]})
        # self.va_labour = pd.DataFrame(va_labour_obj["array"].sum(axis = 1),
                                        #  index = self.dims["USR"][0:len(self.dims["COM"])])
        
        def calc_use_bp_dom(i, use_obj, trade_obj, tradmar_obj, suppmar_obj,make_obj, stocks_obj):
            # Use at delivered prices (including margins)
            ##spread total
            use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
            tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = pd.DataFrame(tradmar).fillna(0)
            margin["Sup_pr"]=suppmar.div(suppmar.sum(axis=0)).fillna(0)
            margin = margin.fillna(0)
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows")
            use_dp_sp_45_47=(use_dp_tr*suppmar_obj["array"][0,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_dp_sp_49_53=(use_dp_tr*suppmar_obj["array"][1,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_bp = use_dp - use_dp_tr
            use_bp.loc["C_45_47"]=use_dp.loc["C_45_47"]+use_dp_sp_45_47
            use_bp.loc["C_49_53"]=use_dp.loc["C_49_53"]+use_dp_sp_49_53
            #spread imports
            use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = margin.fillna(0)
            # Use at basic prices
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
            use_bp_i = use_dp - use_dp_tr
            #total domestic after margins (dom+regions)
            use_bp=use_bp-use_bp_i
            use_bp_exp=use_bp["Exp"]  
            #dom        
            own_reg_share = (trade_obj["array"][:,0,i,i] / trade_obj["array"][:,0,:,i].sum(axis = 1)) 
            u = np.matrix(use_bp)
            use_bp= np.multiply(u, np.matrix(own_reg_share).transpose())
            use_bp= pd.DataFrame(use_bp, columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            #use_bp["Exp"] = use_bp_exp
            #use_bp["Exp"] = use_bp_exp
            make2 = pd.DataFrame(make_obj["array"][:,:,i], columns = make_obj["sets"][1]["dim_desc"], index = make_obj["sets"][0]["dim_desc"])
            cor=make2.sum(axis=1)-use_bp.sum(axis=1)
            exp_dom=pd.DataFrame(np.delete(trade_obj["array"][:,0,i,:], i, axis=1).sum(axis = 1), columns=["EXP"], index=trade_obj["sets"][0]["dim_desc"])
            exp_dom.loc["C_45_47"]=exp_dom.loc["C_45_47"]+np.delete(suppmar_obj["array"][0,:,:,i], i, axis=1).sum()
            exp_dom.loc["C_49_53"]=exp_dom.loc["C_49_53"]+np.delete(suppmar_obj["array"][1,:,:,i], i, axis=1).sum()
            exp_dom.loc["C_45_47"]=cor.loc["C_45_47"]
            exp_dom.loc["C_49_53"]=cor.loc["C_49_53"]  
            use_bp["EXP_REG"] = exp_dom
             
            #Inventories
            stocks=stocks_obj["array"][:,i]
            s=pd.DataFrame(stocks)
            stocks=s.transpose()
            stocks.index=["Stocks"]
            stocks.columns=make_obj["sets"][1]["dim_desc"]
            inv0= make2.div(make2.sum(axis=0), axis = "columns").mul(stocks.loc["Stocks"], axis = "columns")
            inv=inv0.sum(axis=1)
            
            use_bp["Inventories"]=inv
      
            return use_bp

        def calc_use_bp_reg(i, use_obj, trade_obj, tradmar_obj, suppmar_obj):
            use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
            tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = pd.DataFrame(tradmar).fillna(0)
            margin["Sup_pr"]=suppmar.div(suppmar.sum(axis=0)).fillna(0)
            margin = margin.fillna(0)
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows")
            use_dp_sp_45_47=(use_dp_tr*suppmar_obj["array"][0,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_dp_sp_49_53=(use_dp_tr*suppmar_obj["array"][1,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_bp = use_dp - use_dp_tr
            use_bp.loc["C_45_47"]=use_dp.loc["C_45_47"]+use_dp_sp_45_47
            use_bp.loc["C_49_53"]=use_dp.loc["C_49_53"]+use_dp_sp_49_53
            #spread imports
            use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = margin.fillna(0)
            # Use at basic prices
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
            use_bp_i = use_dp - use_dp_tr
            #total domestic after margins (dom+regions)
            use_bp=use_bp-use_bp_i  
            #regions
            own_reg_share = (trade_obj["array"][:,0,i,i] / trade_obj["array"][:,0,:,i].sum(axis = 1))
            u = np.matrix(use_bp)
            use_bp= u - np.multiply(u, np.matrix(own_reg_share).transpose())
            use_bp= pd.DataFrame(use_bp, columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            use_bp["EXP_REG"] = 0
            #use_bp["Exp"] = 0
            use_bp["Inventories"]=0
                          
            return use_bp

        def calc_use_bp_imp(i, use_obj, trade_obj, tradmar_obj):
            # Use at delivered prices (including margins)
            use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"]).fillna(0)
            # Use at basic prices
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
            use_bp = use_dp - use_dp_tr
            use_bp["EXP_REG"] = 0
            use_bp["Inventories"]=0
            return use_bp      
                              
        self.tables = {self.dims["DST"][i]: \
                        useTable(va = pd.DataFrame(\
                                    {taxes_obj["coeff_name"].strip(): taxes_obj["array"][:,:,:,i].sum(axis = (0,1))[0:30],\
                                     va_labour_obj["coeff_name"].strip(): va_labour_obj["array"].sum(axis = 1)[:,i],\
                                     va_capital_obj["coeff_name"].strip(): va_capital_obj["array"][:,i],\
                                     va_land_obj["coeff_name"].strip(): va_land_obj["array"][:,i],\
                                     prodtaxes_obj["coeff_name"].strip(): prodtaxes_obj["array"][:,i]},\
                                     index=self.dims["IND"]).transpose(),\
                                tax_f = pd.DataFrame(np.matrix(taxes_obj["array"][:,:,:,i].sum(axis = (0,1))[30:35]), index=[taxes_obj["coeff_name"].strip()], columns = [use_obj["sets"][2]["dim_desc"][30:35]]),\
                                use_dom = calc_use_bp_dom(i, use_obj, trade_obj, tradmar_obj, suppmar_obj,make_obj, stocks_obj), \
                                use_reg=calc_use_bp_reg(i, use_obj, trade_obj, tradmar_obj, suppmar_obj), \
                                use_imp=calc_use_bp_imp(i, use_obj, trade_obj, tradmar_obj))
                             
                        for i in range(len(self.dims["DST"]))}
 
    def to_excel(self, file):
        writer = pd.ExcelWriter(file, engine='xlsxwriter')
        for key,values in self.tables.items():
                values.table.to_excel(writer, sheet_name = key)
                workbook  = writer.book
                worksheet = writer.sheets[key]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                format.set_num_format('0.000')
                format.set_text_wrap()
                worksheet.set_column(0,41,21, format)
        writer.save()



class useTab_dom:
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
    def __init__(self, use_dom, use_reg, use_imp, va, tax_f):
        self.dims = {"COM": use_dom.index.tolist(), \
                    "ComImp": use_dom.index.tolist() + ["IMP_DOM", "IMP_FOR"],
                    "IND": va.columns.tolist(),
                    "VA": va.index.tolist(),
                    "FINAL": use_dom.columns[range(len(va.columns), len(use_dom.columns))]}
        # Matrices

        self.Ud = use_dom[self.dims["IND"]]
        self.Umdom = use_reg[self.dims["IND"]]
        self.Umdom1=pd.DataFrame(np.matrix(self.Umdom).sum(axis=0), index = ["IMP_REG_USE"], columns = self.dims["IND"])
        self.Umext = use_imp[self.dims["IND"]]
        self.Umext1=pd.DataFrame(np.matrix(self.Umext).sum(axis=0), index = ["IMP_FOR_USE"], columns = self.dims["IND"])
        self.Yd = use_dom[self.dims["FINAL"]]
        self.Ymdom = use_reg[self.dims["FINAL"]]
        self.Ymdom1 = pd.DataFrame(np.matrix(self.Ymdom).sum(axis=0), index = ["IMP_REG_USE"], columns = self.dims["FINAL"])
        self.Ymext = use_imp[self.dims["FINAL"]]
        self.Ymext1 = pd.DataFrame(np.matrix(self.Ymext).sum(axis=0), index = ["IMP_FOR_USE"], columns = self.dims["FINAL"])

        self.W = pd.DataFrame(va)

        tax_f=pd.DataFrame(np.matrix(tax_f))
        K=pd.DataFrame(np.matrix(self.Ud.sum(axis=0)), index=["TOT_USE_DOM"], columns=self.dims["IND"])
        self.Ud=pd.concat([self.Ud, K], axis=0, sort=True)
        self.Uall= pd.concat([pd.DataFrame(self.Ud), self.Umdom1, self.Umext1], axis=0)
        self.table = pd.DataFrame(self.Uall, index=self.dims["COM"] +["TOT_USE_DOM", "IMP_REG_USE", "IMP_FOR_USE"])
        self.table.loc["TAX_SUB"]=self.W.loc["TAXES"]

        K=pd.DataFrame(self.table, columns = self.dims["IND"]) 
        self.table.loc["TOT_INT"]=K.sum(axis=0)-self.table.loc["TOT_USE_DOM"]
        self.table.loc["V1LAB"]=self.W.loc["V1LAB"]
        self.table.loc["V1CAP"]=self.W.loc["V1CAP"]
        self.table.loc["V1LND"]=self.W.loc["V1LND"]
        self.table.loc["V1PTX"]=self.W.loc["V1PTX"]
        self.table.loc["VA"]=self.W.loc["V1LAB"] + self.W.loc["V1CAP"] + self.W.loc["V1LND"]+self.W.loc["V1PTX"]
        self.table.loc["P1R"] = self.table.loc["TOT_INT"]+self.table.loc["VA"]
        self.table["IND_TOT"] = self.table.sum(axis = 1)
       
        K=pd.DataFrame(np.matrix(self.Yd.sum(axis=0)), index=["TOT_USE_DOM"], columns=self.dims["FINAL"])
        self.Yd=pd.concat([self.Yd, K], axis=0, sort=True)

        #self.Yd.loc["TOT_USE_DOM"]=self.Yd.sum(axis=0)
        self.Yall= pd.concat([pd.DataFrame(self.Yd), self.Ymdom1, self.Ymext1], axis=0, sort=True)
        tax_f["EXP_REG"]=0
        tax_f["Inventories"]=0
        tax_f=pd.DataFrame(np.matrix(tax_f), index=["TAX_SUB"], columns= self.dims["FINAL"])
        self.Yall=pd.concat([self.Yall, tax_f], axis=0, sort=True)
        self.Yall.loc["TOT_INT"]=self.Yall.loc["TAX_SUB"]+self.Yall.loc["TOT_USE_DOM"]+self.Yall.loc["IMP_REG_USE"]+self.Yall.loc["IMP_FOR_USE"]
        self.table = pd.concat([self.table, pd.DataFrame(self.Yall, index =self.dims["COM"] +["TOT_USE_DOM", "IMP_REG_USE", "IMP_FOR_USE", "TAX_SUB", "TOT_INT"], columns = self.dims["FINAL"])], axis=1, sort=False)
        K2=pd.DataFrame(self.table, index =self.dims["COM"] +["TOT_USE_DOM", "IMP_REG_USE", "IMP_FOR_USE", "TAX_SUB", "TOT_INT"], columns = self.dims["FINAL"] )
        self.table["FIN_USE"] = K2.sum(axis = 1)
        K2=pd.DataFrame(self.table, index =self.dims["COM"] +["TOT_USE_DOM", "IMP_REG_USE", "IMP_FOR_USE", "TAX_SUB", "TOT_INT"])
        self.table["TOT_USE"] = K2["FIN_USE"]+K2["IND_TOT"]
        

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



class regUseTab_dom:
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

    def __init__(self, use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj, taxes_obj, make_obj, stocks_obj):
        # self.use_pp = use_obj["array"][:,0,0:len(va_labour_obj["sets"][0]["dim_desc"]),:]
        # self.final_pp = use_obj["array"][:,0,len(va_labour_obj["sets"][0]["dim_desc"]):,:]
        self.dims = {k["name"]: k["dim_desc"] for k in use_obj["sets"]}
        self.dims.update({"IND": va_labour_obj["sets"][0]["dim_desc"]})
        # self.va_labour = pd.DataFrame(va_labour_obj["array"].sum(axis = 1),
                                        #  index = self.dims["USR"][0:len(self.dims["COM"])])
        
        def calc_use_bp_dom(i, use_obj, trade_obj, tradmar_obj, suppmar_obj,make_obj, stocks_obj):
            # Use at delivered prices (including margins)
            ##spread total
            use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
            tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = pd.DataFrame(tradmar).fillna(0)
            margin["Sup_pr"]=suppmar.div(suppmar.sum(axis=0)).fillna(0)
            margin = margin.fillna(0)
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows")
            use_dp_sp_45_47=(use_dp_tr*suppmar_obj["array"][0,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_dp_sp_49_53=(use_dp_tr*suppmar_obj["array"][1,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_bp = use_dp - use_dp_tr
            use_bp.loc["C_45_47"]=use_dp.loc["C_45_47"]+use_dp_sp_45_47
            use_bp.loc["C_49_53"]=use_dp.loc["C_49_53"]+use_dp_sp_49_53
            #spread imports
            use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = margin.fillna(0)
            # Use at basic prices
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
            use_bp_i = use_dp - use_dp_tr
            #total domestic after margins (dom+regions)
            use_bp=use_bp-use_bp_i
            use_bp_exp=use_bp["Exp"]  
            #dom        
            own_reg_share = (trade_obj["array"][:,0,i,i] / trade_obj["array"][:,0,:,i].sum(axis = 1)) 
            u = np.matrix(use_bp)
            use_bp= np.multiply(u, np.matrix(own_reg_share).transpose())
            use_bp= pd.DataFrame(use_bp, columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            #use_bp["Exp"] = use_bp_exp
            #use_bp["Exp"] = use_bp_exp
            make2 = pd.DataFrame(make_obj["array"][:,:,i], columns = make_obj["sets"][1]["dim_desc"], index = make_obj["sets"][0]["dim_desc"])
            cor=make2.sum(axis=1)-use_bp.sum(axis=1)
            exp_dom=pd.DataFrame(np.delete(trade_obj["array"][:,0,i,:], i, axis=1).sum(axis = 1), columns=["EXP"], index=trade_obj["sets"][0]["dim_desc"])
            exp_dom.loc["C_45_47"]=exp_dom.loc["C_45_47"]+np.delete(suppmar_obj["array"][0,:,:,i], i, axis=1).sum()
            exp_dom.loc["C_49_53"]=exp_dom.loc["C_49_53"]+np.delete(suppmar_obj["array"][1,:,:,i], i, axis=1).sum()
            exp_dom.loc["C_45_47"]=cor.loc["C_45_47"]
            exp_dom.loc["C_49_53"]=cor.loc["C_49_53"]  
            use_bp["EXP_REG"] = exp_dom
             
            #Inventories
            stocks=stocks_obj["array"][:,i]
            s=pd.DataFrame(stocks)
            stocks=s.transpose()
            stocks.index=["Stocks"]
            stocks.columns=make_obj["sets"][1]["dim_desc"]
            inv0= make2.div(make2.sum(axis=0), axis = "columns").mul(stocks.loc["Stocks"], axis = "columns")
            inv=inv0.sum(axis=1)
            
            use_bp["Inventories"]=inv
      
            return use_bp

        def calc_use_bp_reg(i, use_obj, trade_obj, tradmar_obj, suppmar_obj):
            use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
            tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = pd.DataFrame(tradmar).fillna(0)
            margin["Sup_pr"]=suppmar.div(suppmar.sum(axis=0)).fillna(0)
            margin = margin.fillna(0)
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows")
            use_dp_sp_45_47=(use_dp_tr*suppmar_obj["array"][0,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_dp_sp_49_53=(use_dp_tr*suppmar_obj["array"][1,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_bp = use_dp - use_dp_tr
            use_bp.loc["C_45_47"]=use_dp.loc["C_45_47"]+use_dp_sp_45_47
            use_bp.loc["C_49_53"]=use_dp.loc["C_49_53"]+use_dp_sp_49_53
            #spread imports
            use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = margin.fillna(0)
            # Use at basic prices
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
            use_bp_i = use_dp - use_dp_tr
            #total domestic after margins (dom+regions)
            use_bp=use_bp-use_bp_i  
            #regions
            own_reg_share = (trade_obj["array"][:,0,i,i] / trade_obj["array"][:,0,:,i].sum(axis = 1))
            u = np.matrix(use_bp)
            use_bp= u - np.multiply(u, np.matrix(own_reg_share).transpose())
            use_bp= pd.DataFrame(use_bp, columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            use_bp["EXP_REG"] = 0
            #use_bp["Exp"] = 0
            use_bp["Inventories"]=0
                          
            return use_bp

        def calc_use_bp_imp(i, use_obj, trade_obj, tradmar_obj):
            # Use at delivered prices (including margins)
            use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"]).fillna(0)
            # Use at basic prices
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
            use_bp = use_dp - use_dp_tr
            use_bp["EXP_REG"] = 0
            use_bp["Inventories"]=0
            return use_bp      
                              
        self.tables = {self.dims["DST"][i]: \
                        useTab_dom(va = pd.DataFrame(\
                                    {taxes_obj["coeff_name"].strip(): taxes_obj["array"][:,:,:,i].sum(axis = (0,1))[0:30],\
                                     va_labour_obj["coeff_name"].strip(): va_labour_obj["array"].sum(axis = 1)[:,i],\
                                     va_capital_obj["coeff_name"].strip(): va_capital_obj["array"][:,i],\
                                     va_land_obj["coeff_name"].strip(): va_land_obj["array"][:,i],\
                                     prodtaxes_obj["coeff_name"].strip(): prodtaxes_obj["array"][:,i]},\
                                     index=self.dims["IND"]).transpose(),\
                                tax_f = pd.DataFrame(np.matrix(taxes_obj["array"][:,:,:,i].sum(axis = (0,1))[30:35]), index=[taxes_obj["coeff_name"].strip()], columns = [use_obj["sets"][2]["dim_desc"][30:35]]),\
                                use_dom = calc_use_bp_dom(i, use_obj, trade_obj, tradmar_obj, suppmar_obj,make_obj, stocks_obj), \
                                use_reg=calc_use_bp_reg(i, use_obj, trade_obj, tradmar_obj, suppmar_obj), \
                                use_imp=calc_use_bp_imp(i, use_obj, trade_obj, tradmar_obj))
                             
                        for i in range(len(self.dims["DST"]))}
 
    def to_excel(self, file):
        writer = pd.ExcelWriter(file, engine='xlsxwriter')
        for key,values in self.tables.items():
                values.table.to_excel(writer, sheet_name = key)
                workbook  = writer.book
                worksheet = writer.sheets[key]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                format.set_num_format('0.000')
                format.set_text_wrap()
                worksheet.set_column(0,41,21, format)
        writer.save()




class useTab_reg:
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
    def __init__(self, use_dom, use_reg, use_imp, va):
        self.dims = {"COM": use_dom.index.tolist(), \
                    "ComImp": use_dom.index.tolist() + ["IMP_DOM", "IMP_FOR"],
                    "IND": va.columns.tolist(),
                    "VA": va.index.tolist(),
                    "FINAL": use_dom.columns[range(len(va.columns), len(use_dom.columns))]}
        # Matrices
        self.U = np.matrix(use_dom[self.dims["IND"]])+np.matrix(use_reg[self.dims["IND"]])+np.matrix(use_imp[self.dims["IND"]])
        self.Ud = np.matrix(use_dom[self.dims["IND"]])
        self.Umdom = np.matrix(use_reg[self.dims["IND"]])
        self.Umdom1=pd.DataFrame(np.matrix(use_reg[self.dims["IND"]]).sum(axis=0), index = ["IMP_DOM"], columns = self.dims["IND"])
        self.Umext = np.matrix(use_imp[self.dims["IND"]])
        self.Umext1=pd.DataFrame(np.matrix(use_imp[self.dims["IND"]]).sum(axis=0), index = ["IMP_FOR"], columns = self.dims["IND"])
        self.Y = np.matrix(use_dom[self.dims["FINAL"]])+np.matrix(use_reg[self.dims["FINAL"]])+np.matrix(use_imp[self.dims["FINAL"]])
        self.Yd = np.matrix(use_dom[self.dims["FINAL"]])
        self.Ymdom = np.matrix(use_reg[self.dims["FINAL"]])
        self.Ymdom1 = pd.DataFrame(np.matrix(use_reg[self.dims["FINAL"]]).sum(axis=0), index = ["IMP_DOM"], columns = self.dims["FINAL"])
        self.Ymext = np.matrix(use_imp[self.dims["FINAL"]])
        self.Ymext1 = pd.DataFrame(np.matrix(use_imp[self.dims["FINAL"]]).sum(axis=0), index = ["IMP_FOR"], columns = self.dims["FINAL"])
        self.W = np.matrix(va)
       
        # tables 
 
        self.table = pd.DataFrame(self.Umdom, index = self.dims["COM"], columns = self.dims["IND"])
        self.table["IND_TOT"] = self.table.sum(axis = 1)
        table_int = self.table
        self.table = pd.concat([self.table, pd.DataFrame(self.Ymdom, index = self.dims["COM"], columns = self.dims["FINAL"])], axis=1, sort=True)
        self.table["FIN_USE"] = self.table[self.dims["FINAL"]].sum(axis = 1)
        self.table["TOT_USE"] = self.table["FIN_USE"].add(self.table["IND_TOT"])
        self.table.drop(["EXP_REG", "Inventories"], axis = 1, inplace = True)
        self.table.loc["Prod_total"] = self.table.sum(axis = 0)
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



class regUseTab_reg:
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

    def __init__(self, use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj, taxes_obj, make_obj, stocks_obj):
        # self.use_pp = use_obj["array"][:,0,0:len(va_labour_obj["sets"][0]["dim_desc"]),:]
        # self.final_pp = use_obj["array"][:,0,len(va_labour_obj["sets"][0]["dim_desc"]):,:]
        self.dims = {k["name"]: k["dim_desc"] for k in use_obj["sets"]}
        self.dims.update({"IND": va_labour_obj["sets"][0]["dim_desc"]})
        # self.va_labour = pd.DataFrame(va_labour_obj["array"].sum(axis = 1),
                                        #  index = self.dims["USR"][0:len(self.dims["COM"])])
        
        def calc_use_bp_dom(i, use_obj, trade_obj, tradmar_obj, suppmar_obj,make_obj, stocks_obj):
            # Use at delivered prices (including margins)
            ##spread total
            use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
            tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = pd.DataFrame(tradmar).fillna(0)
            margin["Sup_pr"]=suppmar.div(suppmar.sum(axis=0)).fillna(0)
            margin = margin.fillna(0)
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows")
            use_dp_sp_45_47=(use_dp_tr*suppmar_obj["array"][0,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_dp_sp_49_53=(use_dp_tr*suppmar_obj["array"][1,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_bp = use_dp - use_dp_tr
            use_bp.loc["C_45_47"]=use_dp.loc["C_45_47"]+use_dp_sp_45_47
            use_bp.loc["C_49_53"]=use_dp.loc["C_49_53"]+use_dp_sp_49_53
            #spread imports
            use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = margin.fillna(0)
            # Use at basic prices
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
            use_bp_i = use_dp - use_dp_tr
            #total domestic after margins (dom+regions)
            use_bp=use_bp-use_bp_i
            use_bp_exp=use_bp["Exp"]  
            #dom        
            own_reg_share = (trade_obj["array"][:,0,i,i] / trade_obj["array"][:,0,:,i].sum(axis = 1)) 
            u = np.matrix(use_bp)
            use_bp= np.multiply(u, np.matrix(own_reg_share).transpose())
            use_bp= pd.DataFrame(use_bp, columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            #use_bp["Exp"] = use_bp_exp
            #use_bp["Exp"] = use_bp_exp
            make2 = pd.DataFrame(make_obj["array"][:,:,i], columns = make_obj["sets"][1]["dim_desc"], index = make_obj["sets"][0]["dim_desc"])
            cor=make2.sum(axis=1)-use_bp.sum(axis=1)
            exp_dom=pd.DataFrame(np.delete(trade_obj["array"][:,0,i,:], i, axis=1).sum(axis = 1), columns=["EXP"], index=trade_obj["sets"][0]["dim_desc"])
            exp_dom.loc["C_45_47"]=exp_dom.loc["C_45_47"]+np.delete(suppmar_obj["array"][0,:,:,i], i, axis=1).sum()
            exp_dom.loc["C_49_53"]=exp_dom.loc["C_49_53"]+np.delete(suppmar_obj["array"][1,:,:,i], i, axis=1).sum()
            exp_dom.loc["C_45_47"]=cor.loc["C_45_47"]
            exp_dom.loc["C_49_53"]=cor.loc["C_49_53"]  
            use_bp["EXP_REG"] = exp_dom
             
            #Inventories
            stocks=stocks_obj["array"][:,i]
            s=pd.DataFrame(stocks)
            stocks=s.transpose()
            stocks.index=["Stocks"]
            stocks.columns=make_obj["sets"][1]["dim_desc"]
            inv0= make2.div(make2.sum(axis=0), axis = "columns").mul(stocks.loc["Stocks"], axis = "columns")
            inv=inv0.sum(axis=1)
            
            use_bp["Inventories"]=inv
      
            return use_bp

        def calc_use_bp_reg(i, use_obj, trade_obj, tradmar_obj, suppmar_obj):
            use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
            tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = pd.DataFrame(tradmar).fillna(0)
            margin["Sup_pr"]=suppmar.div(suppmar.sum(axis=0)).fillna(0)
            margin = margin.fillna(0)
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows")
            use_dp_sp_45_47=(use_dp_tr*suppmar_obj["array"][0,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_dp_sp_49_53=(use_dp_tr*suppmar_obj["array"][1,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_bp = use_dp - use_dp_tr
            use_bp.loc["C_45_47"]=use_dp.loc["C_45_47"]+use_dp_sp_45_47
            use_bp.loc["C_49_53"]=use_dp.loc["C_49_53"]+use_dp_sp_49_53
            #spread imports
            use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = margin.fillna(0)
            # Use at basic prices
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
            use_bp_i = use_dp - use_dp_tr
            #total domestic after margins (dom+regions)
            use_bp=use_bp-use_bp_i  
            #regions
            own_reg_share = (trade_obj["array"][:,0,i,i] / trade_obj["array"][:,0,:,i].sum(axis = 1))
            u = np.matrix(use_bp)
            use_bp= u - np.multiply(u, np.matrix(own_reg_share).transpose())
            use_bp= pd.DataFrame(use_bp, columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            use_bp["EXP_REG"] = 0
            #use_bp["Exp"] = 0
            use_bp["Inventories"]=0
                          
            return use_bp

        def calc_use_bp_imp(i, use_obj, trade_obj, tradmar_obj):
            # Use at delivered prices (including margins)
            use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"]).fillna(0)
            # Use at basic prices
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
            use_bp = use_dp - use_dp_tr
            use_bp["EXP_REG"] = 0
            use_bp["Inventories"]=0
            return use_bp      
                              
        self.tables = {self.dims["DST"][i]: \
                        useTab_reg(va = pd.DataFrame(\
                                    {taxes_obj["coeff_name"].strip(): taxes_obj["array"][:,:,:,i].sum(axis = (0,1))[0:30],\
                                     va_labour_obj["coeff_name"].strip(): va_labour_obj["array"].sum(axis = 1)[:,i],\
                                     va_capital_obj["coeff_name"].strip(): va_capital_obj["array"][:,i],\
                                     va_land_obj["coeff_name"].strip(): va_land_obj["array"][:,i],\
                                     prodtaxes_obj["coeff_name"].strip(): prodtaxes_obj["array"][:,i]},\
                                     index=self.dims["IND"]).transpose(),\
                                use_dom = calc_use_bp_dom(i, use_obj, trade_obj, tradmar_obj, suppmar_obj,make_obj, stocks_obj), \
                                use_reg=calc_use_bp_reg(i, use_obj, trade_obj, tradmar_obj, suppmar_obj), \
                                use_imp=calc_use_bp_imp(i, use_obj, trade_obj, tradmar_obj))
                             
                        for i in range(len(self.dims["DST"]))}
 
    def to_excel(self, file):
        writer = pd.ExcelWriter(file, engine='xlsxwriter')
        for key,values in self.tables.items():
                values.table.to_excel(writer, sheet_name = key)
                workbook  = writer.book
                worksheet = writer.sheets[key]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                format.set_num_format('0.000')
                format.set_text_wrap()
                worksheet.set_column(0,41,21, format)
        writer.save()



class useTab_imp:
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
    def __init__(self, use_dom, use_reg, use_imp, va):
        self.dims = {"COM": use_dom.index.tolist(), \
                    "ComImp": use_dom.index.tolist() + ["IMP_DOM", "IMP_FOR"],
                    "IND": va.columns.tolist(),
                    "VA": va.index.tolist(),
                    "FINAL": use_dom.columns[range(len(va.columns), len(use_dom.columns))]}
        # Matrices
        self.U = np.matrix(use_dom[self.dims["IND"]])+np.matrix(use_reg[self.dims["IND"]])+np.matrix(use_imp[self.dims["IND"]])
        self.Ud = np.matrix(use_dom[self.dims["IND"]])
        self.Umdom = np.matrix(use_reg[self.dims["IND"]])
        self.Umdom1=pd.DataFrame(np.matrix(use_reg[self.dims["IND"]]).sum(axis=0), index = ["IMP_DOM"], columns = self.dims["IND"])
        self.Umext = np.matrix(use_imp[self.dims["IND"]])
        self.Umext1=pd.DataFrame(np.matrix(use_imp[self.dims["IND"]]).sum(axis=0), index = ["IMP_FOR"], columns = self.dims["IND"])
        self.Y = np.matrix(use_dom[self.dims["FINAL"]])+np.matrix(use_reg[self.dims["FINAL"]])+np.matrix(use_imp[self.dims["FINAL"]])
        self.Yd = np.matrix(use_dom[self.dims["FINAL"]])
        self.Ymdom = np.matrix(use_reg[self.dims["FINAL"]])
        self.Ymdom1 = pd.DataFrame(np.matrix(use_reg[self.dims["FINAL"]]).sum(axis=0), index = ["IMP_DOM"], columns = self.dims["FINAL"])
        self.Ymext = np.matrix(use_imp[self.dims["FINAL"]])
        self.Ymext1 = pd.DataFrame(np.matrix(use_imp[self.dims["FINAL"]]).sum(axis=0), index = ["IMP_FOR"], columns = self.dims["FINAL"])
        self.W = np.matrix(va)
       
        # tables 
        self.table = pd.DataFrame(self.Umext, index = self.dims["COM"], columns = self.dims["IND"])
        self.table["IND_TOT"] = self.table.sum(axis = 1)
        self.table = pd.concat([self.table, pd.DataFrame(self.Ymext, index = self.dims["COM"], columns = self.dims["FINAL"])], axis=1, sort=True)
        self.table["FIN_USE"] = self.table[self.dims["FINAL"]].sum(axis = 1)
        self.table["TOT_USE"] = self.table["FIN_USE"].add(self.table["IND_TOT"])
        self.table.drop(["EXP_REG", "Inventories"], axis = 1, inplace = True)
        self.table.loc["Prod_total"] = self.table.sum(axis = 0)
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



class regUseTab_imp:
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

    def __init__(self, use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj, taxes_obj, make_obj, stocks_obj):
        # self.use_pp = use_obj["array"][:,0,0:len(va_labour_obj["sets"][0]["dim_desc"]),:]
        # self.final_pp = use_obj["array"][:,0,len(va_labour_obj["sets"][0]["dim_desc"]):,:]
        self.dims = {k["name"]: k["dim_desc"] for k in use_obj["sets"]}
        self.dims.update({"IND": va_labour_obj["sets"][0]["dim_desc"]})
        # self.va_labour = pd.DataFrame(va_labour_obj["array"].sum(axis = 1),
                                        #  index = self.dims["USR"][0:len(self.dims["COM"])])
        
        def calc_use_bp_dom(i, use_obj, trade_obj, tradmar_obj, suppmar_obj,make_obj, stocks_obj):
            # Use at delivered prices (including margins)
            ##spread total
            use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
            tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = pd.DataFrame(tradmar).fillna(0)
            margin["Sup_pr"]=suppmar.div(suppmar.sum(axis=0)).fillna(0)
            margin = margin.fillna(0)
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows")
            use_dp_sp_45_47=(use_dp_tr*suppmar_obj["array"][0,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_dp_sp_49_53=(use_dp_tr*suppmar_obj["array"][1,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_bp = use_dp - use_dp_tr
            use_bp.loc["C_45_47"]=use_dp.loc["C_45_47"]+use_dp_sp_45_47
            use_bp.loc["C_49_53"]=use_dp.loc["C_49_53"]+use_dp_sp_49_53
            #spread imports
            use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = margin.fillna(0)
            # Use at basic prices
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
            use_bp_i = use_dp - use_dp_tr
            #total domestic after margins (dom+regions)
            use_bp=use_bp-use_bp_i
            use_bp_exp=use_bp["Exp"]  
            #dom        
            own_reg_share = (trade_obj["array"][:,0,i,i] / trade_obj["array"][:,0,:,i].sum(axis = 1)) 
            u = np.matrix(use_bp)
            use_bp= np.multiply(u, np.matrix(own_reg_share).transpose())
            use_bp= pd.DataFrame(use_bp, columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            #use_bp["Exp"] = use_bp_exp
            #use_bp["Exp"] = use_bp_exp
            make2 = pd.DataFrame(make_obj["array"][:,:,i], columns = make_obj["sets"][1]["dim_desc"], index = make_obj["sets"][0]["dim_desc"])
            cor=make2.sum(axis=1)-use_bp.sum(axis=1)
            exp_dom=pd.DataFrame(np.delete(trade_obj["array"][:,0,i,:], i, axis=1).sum(axis = 1), columns=["EXP"], index=trade_obj["sets"][0]["dim_desc"])
            exp_dom.loc["C_45_47"]=exp_dom.loc["C_45_47"]+np.delete(suppmar_obj["array"][0,:,:,i], i, axis=1).sum()
            exp_dom.loc["C_49_53"]=exp_dom.loc["C_49_53"]+np.delete(suppmar_obj["array"][1,:,:,i], i, axis=1).sum()
            exp_dom.loc["C_45_47"]=cor.loc["C_45_47"]
            exp_dom.loc["C_49_53"]=cor.loc["C_49_53"]  
            use_bp["EXP_REG"] = exp_dom
             
            #Inventories
            stocks=stocks_obj["array"][:,i]
            s=pd.DataFrame(stocks)
            stocks=s.transpose()
            stocks.index=["Stocks"]
            stocks.columns=make_obj["sets"][1]["dim_desc"]
            inv0= make2.div(make2.sum(axis=0), axis = "columns").mul(stocks.loc["Stocks"], axis = "columns")
            inv=inv0.sum(axis=1)
            
            use_bp["Inventories"]=inv
      
            return use_bp

        def calc_use_bp_reg(i, use_obj, trade_obj, tradmar_obj, suppmar_obj):
            use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
            tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = pd.DataFrame(tradmar).fillna(0)
            margin["Sup_pr"]=suppmar.div(suppmar.sum(axis=0)).fillna(0)
            margin = margin.fillna(0)
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows")
            use_dp_sp_45_47=(use_dp_tr*suppmar_obj["array"][0,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_dp_sp_49_53=(use_dp_tr*suppmar_obj["array"][1,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
            use_bp = use_dp - use_dp_tr
            use_bp.loc["C_45_47"]=use_dp.loc["C_45_47"]+use_dp_sp_45_47
            use_bp.loc["C_49_53"]=use_dp.loc["C_49_53"]+use_dp_sp_49_53
            #spread imports
            use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
            margin = margin.fillna(0)
            # Use at basic prices
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
            use_bp_i = use_dp - use_dp_tr
            #total domestic after margins (dom+regions)
            use_bp=use_bp-use_bp_i  
            #regions
            own_reg_share = (trade_obj["array"][:,0,i,i] / trade_obj["array"][:,0,:,i].sum(axis = 1))
            u = np.matrix(use_bp)
            use_bp= u - np.multiply(u, np.matrix(own_reg_share).transpose())
            use_bp= pd.DataFrame(use_bp, columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            use_bp["EXP_REG"] = 0
            #use_bp["Exp"] = 0
            use_bp["Inventories"]=0
                          
            return use_bp

        def calc_use_bp_imp(i, use_obj, trade_obj, tradmar_obj):
            # Use at delivered prices (including margins)
            use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
            margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"]).fillna(0)
            # Use at basic prices
            use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
            use_bp = use_dp - use_dp_tr
            use_bp["EXP_REG"] = 0
            use_bp["Inventories"]=0
            return use_bp      
                              
        self.tables = {self.dims["DST"][i]: \
                        useTab_imp(va = pd.DataFrame(\
                                    {taxes_obj["coeff_name"].strip(): taxes_obj["array"][:,:,:,i].sum(axis = (0,1))[0:30],\
                                     va_labour_obj["coeff_name"].strip(): va_labour_obj["array"].sum(axis = 1)[:,i],\
                                     va_capital_obj["coeff_name"].strip(): va_capital_obj["array"][:,i],\
                                     va_land_obj["coeff_name"].strip(): va_land_obj["array"][:,i],\
                                     prodtaxes_obj["coeff_name"].strip(): prodtaxes_obj["array"][:,i]},\
                                     index=self.dims["IND"]).transpose(),\
                                use_dom = calc_use_bp_dom(i, use_obj, trade_obj, tradmar_obj, suppmar_obj,make_obj, stocks_obj), \
                                use_reg=calc_use_bp_reg(i, use_obj, trade_obj, tradmar_obj, suppmar_obj), \
                                use_imp=calc_use_bp_imp(i, use_obj, trade_obj, tradmar_obj))
                             
                        for i in range(len(self.dims["DST"]))}
 
    def to_excel(self, file):
        writer = pd.ExcelWriter(file, engine='xlsxwriter')
        for key,values in self.tables.items():
                values.table.to_excel(writer, sheet_name = key)
                workbook  = writer.book
                worksheet = writer.sheets[key]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                format.set_num_format('0.000')
                format.set_text_wrap()
                worksheet.set_column(0,41,21, format)
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
    
    def __init__(self, B, F, W, use_tab):
        self.B = np.matrix(B)
        self.F = np.matrix(F)
        self.W = np.matrix(W)
        self.table = B
        self.table = pd.concat([B, W], sort=True)
        self.table = pd.concat([self.table, F], axis = 1, sort=True)
        self.table = self.table.loc[B.index.tolist() + W.index.tolist(), B.columns.tolist() + F.columns.tolist()]   # to original order
        self.table.loc["Sum"] = pd.DataFrame(B, columns=use_tab.dims["IND"]).sum(axis = 0)+pd.DataFrame(W, columns=use_tab.dims["IND"]).sum(axis = 0)
        self.table["Sum"] = self.table.sum(axis=1)
        
        #self.table.loc["Sum"] = self.table.sum(axis=0)
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
            Bd = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Ud
            Bmdom = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Umdom
            Bmext = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Umext
            # F = T * Y = V * inv(diag(q)) * Y

            Fd = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Yd
            Fmdom = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Ymdom
            F_d_r=Fd+Fmdom
            Fmext = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Ymext
            F_y = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Y
            W = use_tab.W  

            B = pd.DataFrame(Bd, index=use_tab.dims["COM"], columns=use_tab.dims["IND"])
            B.loc["Domestic_import"] = pd.DataFrame(Bmdom, columns=use_tab.dims["IND"]).sum(axis = 0)
            B.loc["External_import"] = pd.DataFrame(Bmext, columns=use_tab.dims["IND"]).sum(axis = 0)

            F = pd.DataFrame(Fd, index=use_tab.dims["COM"], columns=use_tab.dims["FINAL"])
            #F.loc["Domestic_import"] = pd.DataFrame(Fmdom, columns=use_tab.dims["FINAL"]).sum(axis = 0)
            #F.loc["External_import"] = pd.DataFrame(Fmext, columns=use_tab.dims["FINAL"]).sum(axis = 0)
            
            ###############3
            #B_t=Bd+Bmdom+Bmext
            B = pd.DataFrame(B, columns=use_tab.dims["IND"])
            #F_t=Fd+Fmdom+Fmext
            F = pd.DataFrame(F, columns=use_tab.dims["FINAL"])
            #F["Sum"]=pd.DataFrame(F, index=use_tab.dims["COM"], columns=use_tab.dims["FINAL"]).sum(axis=1)+pd.DataFrame(B, index=use_tab.dims["COM"], columns=use_tab.dims["IND"]).sum(axis=1)
            W = pd.DataFrame(W, index=use_tab.dims["VA"], columns=use_tab.dims["IND"])
            #W.loc["Sum"] = pd.DataFrame(B, columns=use_tab.dims["IND"]).sum(axis = 0)+pd.DataFrame(W, columns=use_tab.dims["IND"]).sum(axis = 0)
            return IOTable(B, F, W, use_tab)  

        self.tables = {i : build_io(sup.tables[i], use.tables[i]) \
                        for i in sup.tables.keys()}

    def to_excel(self, file):
        writer = pd.ExcelWriter(file, engine='xlsxwriter')
        for key,values in self.tables.items():
                values.table.to_excel(writer, sheet_name = key)
                workbook  = writer.book
                worksheet = writer.sheets[key]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                format.set_num_format('0.000')
                format.set_text_wrap()
                worksheet.set_column(0,41,21, format)
        writer.save()



class IOTable_reg:
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
    
    def __init__(self, B, F):
        self.B = np.matrix(B)
        self.F = np.matrix(F)

        self.table = B
      
        self.table = pd.concat([self.table, F], axis = 1, sort=True)
        self.table = self.table.loc[B.index.tolist(), B.columns.tolist() + F.columns.tolist()]   # to original order
        self.table["SUM"]=self.table.sum(axis=1)
        self.table.loc["SUM"]=self.table.sum(axis=0)


class regIOtables_reg:
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
            Bd = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Ud
            Bmdom = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Umdom
            Bmext = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Umext
            # F = T * Y = V * inv(diag(q)) * Y

            Fd = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Yd
            Fmdom = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Ymdom
            F_d_r=Fd+Fmdom
            Fmext = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Ymext
            F_y = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Y
            

            B = pd.DataFrame(Bmdom, index=use_tab.dims["COM"], columns=use_tab.dims["IND"])

            F = pd.DataFrame(Fmdom, index=use_tab.dims["COM"], columns=use_tab.dims["FINAL"])
  ###############3
            #B_t=Bd+Bmdom+Bmext
            B = pd.DataFrame(B, columns=use_tab.dims["IND"])
            #F_t=Fd+Fmdom+Fmext
            F = pd.DataFrame(F, columns=use_tab.dims["FINAL"])
            #F["Sum"]=pd.DataFrame(F, index=use_tab.dims["COM"], columns=use_tab.dims["FINAL"]).sum(axis=1)+pd.DataFrame(B, index=use_tab.dims["COM"], columns=use_tab.dims["IND"]).sum(axis=1)
            F.drop(["EXP_REG", "Inventories"], axis = 1, inplace = True)
            #B.loc["Sum"] = pd.DataFrame(B, columns=use_tab.dims["IND"]).sum(axis = 0)
            return IOTable_reg(B, F)  

        self.tables = {i : build_io(sup.tables[i], use.tables[i]) \
                        for i in sup.tables.keys()}

    def to_excel(self, file):
        writer = pd.ExcelWriter(file, engine='xlsxwriter')
        for key,values in self.tables.items():
                values.table.to_excel(writer, sheet_name = key)
                workbook  = writer.book
                worksheet = writer.sheets[key]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                format.set_num_format('0.000')
                format.set_text_wrap()
                worksheet.set_column(0,41,21, format)
        writer.save()

class IOTable_imp:
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
    
    def __init__(self, B, F):
        self.B = np.matrix(B)
        self.F = np.matrix(F)

        self.table = B
      
        self.table = pd.concat([self.table, F], axis = 1, sort=True)
        self.table = self.table.loc[B.index.tolist(), B.columns.tolist() + F.columns.tolist()]   # to original order
        self.table["SUM"]=self.table.sum(axis=1)
        self.table.loc["SUM"]=self.table.sum(axis=0)


class regIOtables_imp:
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
            tax_f=use_tab.tax_f
            Bd = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Ud
            Bmdom = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Umdom
            Bmext = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Umext
            # F = T * Y = V * inv(diag(q)) * Y

            Fd = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Yd
            Fmdom = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Ymdom
            F_d_r=Fd+Fmdom
            Fmext = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Ymext
            F_y = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Y
            

            B = pd.DataFrame(Bmext, index=use_tab.dims["COM"], columns=use_tab.dims["IND"])

            F = pd.DataFrame(Fmext, index=use_tab.dims["COM"], columns=use_tab.dims["FINAL"])
  ###############3
            #B_t=Bd+Bmdom+Bmext
            B = pd.DataFrame(B, columns=use_tab.dims["IND"])
            #F_t=Fd+Fmdom+Fmext
            F = pd.DataFrame(F, columns=use_tab.dims["FINAL"])
            #F["Sum"]=pd.DataFrame(F, index=use_tab.dims["COM"], columns=use_tab.dims["FINAL"]).sum(axis=1)+pd.DataFrame(B, index=use_tab.dims["COM"], columns=use_tab.dims["IND"]).sum(axis=1)
            F.drop(["EXP_REG", "Inventories"], axis = 1, inplace = True)
            #B.loc["Sum"] = pd.DataFrame(B, columns=use_tab.dims["IND"]).sum(axis = 0)
            return IOTable_imp(B, F)  

        self.tables = {i : build_io(sup.tables[i], use.tables[i]) \
                        for i in sup.tables.keys()}

    def to_excel(self, file):
        writer = pd.ExcelWriter(file, engine='xlsxwriter')
        for key,values in self.tables.items():
                values.table.to_excel(writer, sheet_name = key)
                workbook  = writer.book
                worksheet = writer.sheets[key]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                format.set_num_format('0.000')
                format.set_text_wrap()
                worksheet.set_column(0,41,21, format)
        writer.save()

class IOTable_coef:
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
    
    def __init__(self, Ad, Amdom, Amext, R, use_tab):
        self.Ad=Ad
        self.Amdom=Amdom
        self.Amext=Amext
        self.At=Ad+Amdom+Amext
        self.table = Ad
        self.table.loc["IND_TOT"]=pd.DataFrame(Ad, columns=use_tab.dims["IND"]).sum(axis = 0)
        self.table.loc["IMP_REG_USE"] = pd.DataFrame(Amdom, columns=use_tab.dims["IND"]).sum(axis = 0)
        self.table.loc["IMP_FOR_USE"]= pd.DataFrame(Amext, columns=use_tab.dims["IND"]).sum(axis = 0)
        self.table.loc["TAX_SUB"]=R.loc["TAXES"]
        self.table.loc["TOT_INT"]=self.table.sum(axis=0)-self.table.loc["IND_TOT"]
        self.table.loc["V1LAB"]=R.loc["V1LAB"]
        self.table.loc["V1CAP"]=R.loc["V1CAP"]
        self.table.loc["V1LND"]=R.loc["V1LND"]
        self.table.loc["V1PTX"]=R.loc["V1PTX"]
        self.table.loc["VA"]=R.loc["V1LAB"] + R.loc["V1CAP"] + R.loc["V1LND"]+R.loc["V1PTX"]
        self.table.loc["P1R"] = self.table.loc["TOT_INT"]+self.table.loc["VA"]
        
        #self.table.loc["Sum"] = self.table.sum(axis=0)

        
class regIOtables_coef:
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
            # A = T * U * * inv(diag(g))
            Ad=sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Ud* np.linalg.inv(np.diagflat(sup_tab.gt.transpose())) 
            Amdom=sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Umdom* np.linalg.inv(np.diagflat(sup_tab.gt.transpose())) 
            Amext=sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Umext* np.linalg.inv(np.diagflat(sup_tab.gt.transpose())) 

            R = use_tab.W * np.linalg.inv(np.diagflat(sup_tab.gt.transpose()))   

            Ad = pd.DataFrame(Ad, index=use_tab.dims["COM"], columns=use_tab.dims["IND"])
            Amdom = pd.DataFrame(Amdom, index=use_tab.dims["COM"], columns=use_tab.dims["IND"])
            Amext = pd.DataFrame(Amext, index=use_tab.dims["COM"], columns=use_tab.dims["IND"])
            R = pd.DataFrame(R, index=use_tab.dims["VA"], columns=use_tab.dims["IND"])
            return IOTable_coef(Ad, Amdom, Amext, R, use_tab)  

        self.tables = {i : build_io(sup.tables[i], use.tables[i]) \
                        for i in sup.tables.keys()}
 
    def to_excel(self, file):
        writer = pd.ExcelWriter(file, engine='xlsxwriter')
        for key,values in self.tables.items():
                values.table.to_excel(writer, sheet_name = key)
                workbook  = writer.book
                worksheet = writer.sheets[key]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                format.set_num_format('0.000')
                format.set_text_wrap()
                worksheet.set_column(0,41,25, format)
        writer.save()



class IOTable2:
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
    
    def __init__(self, B, Bmdom, Bmext, F, Fmdom, Fmext, W, use_tab):


        self.Bd = B
        self.Bmdom = Bmdom
        self.Bmdom1=pd.DataFrame(np.matrix(Bmdom).sum(axis=0), index = ["IMP_REG_USE"], columns = use_tab.dims["IND"])
        self.Bmext = Bmext
        self.Bmext1=pd.DataFrame(np.matrix(Bmext).sum(axis=0), index = ["IMP_FOR_USE"], columns = use_tab.dims["IND"])
        
        self.Fd = F
        self.Fmdom = Fmdom
        self.Fmdom1 = pd.DataFrame(np.matrix(Fmdom).sum(axis=0), index = ["IMP_REG_USE"], columns = use_tab.dims["FINAL"])
        self.Fmext = Fmext
        self.Fmext1 = pd.DataFrame(np.matrix(Fmext).sum(axis=0), index = ["IMP_FOR_USE"], columns = use_tab.dims["FINAL"])
        self.W = W
       
        # tables
        self.Bd.loc["TOT_USE_DOM"]=self.Bd.sum(axis=0)
        
        self.Ball= pd.concat([pd.DataFrame(self.Bd), self.Bmdom1, self.Bmext1], axis=0)
           
        self.table = pd.DataFrame(self.Ball, index=use_tab.dims["COM"] +["TOT_USE_DOM", "IMP_REG_USE", "IMP_FOR_USE"])
        
        
        self.table.loc["TAX_SUB"]=W.loc["TAXES"]
        K=pd.DataFrame(self.table, columns = use_tab.dims["IND"]) 
        self.table.loc["TOT_INT"]=K.sum(axis=0)-self.table.loc["TOT_USE_DOM"]
        self.table.loc["V1LAB"]=W.loc["V1LAB"]
        self.table.loc["V1CAP"]=W.loc["V1CAP"]
        self.table.loc["V1LND"]=W.loc["V1LND"]
        self.table.loc["V1PTX"]=W.loc["V1PTX"]
        self.table.loc["VA"]=W.loc["V1LAB"] + W.loc["V1CAP"] + W.loc["V1LND"]+W.loc["V1PTX"]
        self.table.loc["P1R"] = self.table.loc["TOT_INT"]+self.table.loc["VA"]
        self.table["IND_TOT"] = self.table.sum(axis = 1)
        self.Fd.loc["TOT_USE_DOM"]=self.Fd.sum(axis=0)
        self.Fall= pd.concat([pd.DataFrame(self.Fd), self.Fmdom1, self.Fmext1], axis=0, sort=True)

        tax_f=pd.DataFrame(np.matrix(use_tab.tax_f))
        tax_f["EXP_REG"]=0
        tax_f["Inventories"]=0
        tax_f=pd.DataFrame(np.matrix(tax_f), index=["TAX_SUB"], columns= use_tab.dims["FINAL"])
        self.Fall=pd.concat([self.Fall, tax_f], axis=0, sort=True)
        self.Fall.loc["TOT_INT"]=self.Fall.loc["TAX_SUB"]+self.Fall.loc["TOT_USE_DOM"]+self.Fall.loc["IMP_REG_USE"]+self.Fall.loc["IMP_FOR_USE"]
        self.table = pd.concat([self.table, pd.DataFrame(self.Fall, index =use_tab.dims["COM"] +["TOT_USE_DOM", "IMP_REG_USE", "IMP_FOR_USE", "TAX_SUB", "TOT_INT"], columns = use_tab.dims["FINAL"])], axis=1, sort=False)
        K2=pd.DataFrame(self.table, index =use_tab.dims["COM"] +["TOT_USE_DOM", "IMP_REG_USE", "IMP_FOR_USE", "TAX_SUB", "TOT_INT"], columns = use_tab.dims["FINAL"] )
        self.table["FIN_USE"] = K2.sum(axis = 1)
        K2=pd.DataFrame(self.table, index =use_tab.dims["COM"] +["TOT_USE_DOM", "IMP_REG_USE", "IMP_FOR_USE", "TAX_SUB", "TOT_INT"])
        self.table["TOT_USE"] = K2["FIN_USE"]+K2["IND_TOT"]
       

class regIOtables2:
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
            Bd = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Ud
            Bmdom = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Umdom
            Bmext = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Umext
            # F = T * Y = V * inv(diag(q)) * Y
            
            Fd = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Yd
            Fmdom = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Ymdom
            F_d_r=Fd+Fmdom
            Fmext = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Ymext
            F_y = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.Y
            W = pd.DataFrame(use_tab.W, index=use_tab.dims["VA"], columns=use_tab.dims["IND"])

            B = pd.DataFrame(Bd, index=use_tab.dims["COM"], columns=use_tab.dims["IND"])
            Bmdom = pd.DataFrame(Bmdom, index=use_tab.dims["COM"], columns=use_tab.dims["IND"])
            Bmext = pd.DataFrame(Bmext, index=use_tab.dims["COM"], columns=use_tab.dims["IND"])
            #B.loc["Domestic_import"] = pd.DataFrame(Bmdom, columns=use_tab.dims["IND"]).sum(axis = 0)
            #B.loc["External_import"] = pd.DataFrame(Bmext, columns=use_tab.dims["IND"]).sum(axis = 0)

            F = pd.DataFrame(Fd, index=use_tab.dims["COM"], columns=use_tab.dims["FINAL"])
            Fmdom = pd.DataFrame(Fmdom, index=use_tab.dims["COM"], columns=use_tab.dims["FINAL"])
            Fmext = pd.DataFrame(Fmext, index=use_tab.dims["COM"], columns=use_tab.dims["FINAL"])
            #F.loc["Domestic_import"] = pd.DataFrame(Fmdom, columns=use_tab.dims["FINAL"]).sum(axis = 0)
            #F.loc["External_import"] = pd.DataFrame(Fmext, columns=use_tab.dims["FINAL"]).sum(axis = 0)
            

            return IOTable2(B, Bmdom, Bmext, F, Fmdom, Fmext, W, use_tab)  

        self.tables = {i : build_io(sup.tables[i], use.tables[i]) \
                        for i in sup.tables.keys()}

    def to_excel(self, file):
        writer = pd.ExcelWriter(file, engine='xlsxwriter')
        for key,values in self.tables.items():
                values.table.to_excel(writer, sheet_name = key)
                workbook  = writer.book
                worksheet = writer.sheets[key]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                format.set_num_format('0.000')
                format.set_text_wrap()
                worksheet.set_column(0,41,21, format)
        writer.save()

def translate_reg_tables(tables, trans_file_init, lang = "fi"):
        """
        Translate table from codes.

         Parameters
        ----------
        tables: object for regtable classes
        trans_file_init: str
                A initial part of the tranlastion csv-files in the translate folder. ie before _index and _columns appendix.
        lang: str
                A column name in tranlate files.
        """
        tran_col = pd.read_csv("translate/" + trans_file_init + "_columns.csv", sep=";", encoding="latin_1")
        tran_ind = pd.read_csv("translate/" + trans_file_init + "_index.csv", sep=";", encoding="latin_1")
        y = copy.deepcopy(tables)
        for i in y.tables.keys():
                y.tables[i].table.rename(index = dict(zip(tran_ind["index"], tran_ind[lang])), columns = dict(zip(tran_col["columns"], tran_col[lang])), inplace = True)
        return y

def to_long_table(tables):
        """
        From wide to long form

         Parameters
        ----------
        tables: object for regtable classes

        """
        long_table = pd.DataFrame()
        for r in tables.tables.keys():
                long = tables.tables[r].table.copy()
                long["REG"] = r
                long["COM"] = long.index
                long = long.melt(id_vars = ["REG", "COM"], var_name = "IND")
                long_table = long_table.append(long, sort=False)
        return long_table

