# -*- coding: utf-8 -*-
"""
Report regional input output tables

@author: jh

"""

import pandas as pd
import numpy as np
import har2output5 as ho
import os

import importlib
importlib.reload(ho)

import harpy

# HARPY module by Centre of Policy Studies for writing data into Header Array (HAR) format.
# Available at https://github.com/GEMPACKsoftware/HARPY
from harpy.har_file import HarFileObj

harFolder = "hardata"
termFolder = "TERM"


# Read premod har-file that includes regionalized data
premod = harpy.HarFileObj.loadFromDisk(termFolder+"/premod.har")

#Read basedata30 where Exports from Imports Use Table is located
base30 = harpy.HarFileObj.loadFromDisk(harFolder+"/basedata30.har")


#Read Exports from Imports Use Table (re-exports) into use_e
use_e = base30.getHeaderArrayObj("4BAI")

# objects from premod
make_obj = premod.getHeaderArrayObj("MAKE")
use_obj = premod.getHeaderArrayObj("BSMR")
va_labour_obj = premod.getHeaderArrayObj("1LAB")
va_capital_obj = premod.getHeaderArrayObj("1CAP")
va_land_obj = premod.getHeaderArrayObj("1LND")
trade_obj = premod.getHeaderArrayObj("TRAD")
tradmar_obj = premod.getHeaderArrayObj("TMAR")
suppmar_obj = premod.getHeaderArrayObj("MARS")
taxes_obj = premod.getHeaderArrayObj("UTAX")
stocks_obj = premod.getHeaderArrayObj("STOK")
prodtaxes_obj = premod.getHeaderArrayObj("1PTX")


# Derive Exports in Imports Use table (Exp_imp) for regions based on shares of domestic Exports (exports in domestic use table);
# This is a regionalization of Exp_imp alongside domestic Exports' regionalization strategy;
#Regionalization is in loops for region 'j' in comodity 'i';
#Note that column 33 is exports in use tables;
# Exp_imp for comodity 'i' = (Domestic Export(i) in region j) /[National_export_domestic(i)]*National Exp_imp(i) 
for j in range(0,19):
    for i in range(0,30):
        use_obj["array"][i,1,33,j]=use_obj["array"][i,0,33,j]/(use_obj["array"][i,0,33,:].sum()+0.000001)*use_e["array"][i] 




importlib.reload(ho)

#Supply table
reg_supp = ho.regSupplyTables(make_obj, use_obj, tradmar_obj, suppmar_obj, trade_obj, stocks_obj)
reg_supp.to_excel(file = "outdata/test_supp2014_5.xlsx")

#use Table - total
reg_use = ho.regUseTables(use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj, taxes_obj, make_obj, stocks_obj)
reg_use.to_excel(file = "outdata/test_use2014_5.xlsx")

#use Table - domestic
reg_use_dom = ho.regUseTab_dom(use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj, taxes_obj, make_obj, stocks_obj)
reg_use_dom.to_excel(file = "outdata/test_use_dom2014_5.xlsx")

#use Table - regional
reg_use_reg = ho.regUseTab_reg(use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj, taxes_obj, make_obj, stocks_obj)
reg_use_reg.to_excel(file = "outdata/test_use_reg2014_5.xlsx")

#use Table - foreign imports
reg_use_imp = ho.regUseTab_imp(use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj, taxes_obj, make_obj, stocks_obj)
reg_use_imp.to_excel(file = "outdata/test_use_imp2014_5.xlsx")

#I-O table domestic
reg_io = ho.regIOtables(reg_supp, reg_use)
reg_io.to_excel(file = "outdata/test_io2014_5.xlsx")
 
#I-O table regional
reg_io_reg = ho.regIOtables_reg(reg_supp, reg_use)
reg_io_reg.to_excel(file = "outdata/test_io_reg2014_5.xlsx")

#I-O table foreign imports
reg_io_imp = ho.regIOtables_imp(reg_supp, reg_use)
reg_io_imp.to_excel(file = "outdata/test_io_imp2014_5.xlsx")


reg_io_coef = ho.regIOtables_coef(reg_supp, reg_use)
reg_io_coef.to_excel(file = "outdata/test_io_imp2014_5.xlsx")
#TEST UUSIMA

i=0
##################################################################################
#USE DOM
 
use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
margin = pd.DataFrame(tradmar, axis=1)).fillna(0)
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
make2 = pd.DataFrame(make_obj["array"][:,:,i], columns = make_obj["sets"][1]["dim_desc"], index = make_obj["sets"][0]["dim_desc"])
cor=make2.sum(axis=1)-use_bp.sum(axis=1)


exp_dom=pd.DataFrame(np.delete(trade_obj["array"][:,0,i,:], i, axis=1).sum(axis = 1), columns=["EXP"], index=trade_obj["sets"][0]["dim_desc"])
exp_dom.loc["C_45_47"]=exp_dom.loc["C_45_47"]+np.delete(suppmar_obj["array"][0,:,:,i], i, axis=1).sum()
exp_dom.loc["C_49_53"]=exp_dom.loc["C_49_53"]+np.delete(suppmar_obj["array"][1,:,:,i], i, axis=1).sum()
exp_dom.loc["C_45_47"]=cor.loc["C_45_47"]
exp_dom.loc["C_49_53"]=cor.loc["C_49_53"]  
use_bp["Exp_dom"] = exp_dom
#Inventories
stocks=stocks_obj["array"][:,i]
s=pd.DataFrame(stocks)
stocks=s.transpose()
stocks.index=["Stocks"]
stocks.columns=make_obj["sets"][1]["dim_desc"]
inv0= make2.div(make2.sum(axis=0), axis = "columns").mul(stocks.loc["Stocks"], axis = "columns")
inv=inv0.sum(axis=1)
            
use_bp["IVENTORIES"]=inv
use_bp_dom=use_bp
      
 
#USE REG
use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
# Margins
suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
margin = pd.DataFrame(pd.concat([tradmar, suppmar], axis=1)).fillna(0)
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
use_bp["Exp_dom"] = 0
#use_bp["Exp"] = 0
use_bp["IVENTORIES"]=0
use_bp_reg=use_bp

#USE IMP

# Use at delivered prices (including margins)
use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
# Margins
margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"]).fillna(0)
# Use at basic prices
use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
use_bp = use_dp - use_dp_tr
use_bp["Exp_dom"] = 0
use_bp["IVENTORIES"]=0
use_imp=use_bp
use_imp1=use_imp
use_imp.drop([use_imp.columns[-1],use_imp.columns[-2]], axis=1)

use_bp_dom.sum(axis=1)
use_bp_dom.sum(axis=1)
dims = {"COM": use_bp_dom.index.tolist(), \
        "ComImp": use_bp_dom.index.tolist() + ["Domestic imports", "Foreign imports"],
        "FINAL": use_bp_dom.index.tolist()}
dims["FINAL"]
#Chosen path. Aming for this + correction for sup margin ()
##################################

make_obj["array"][:,:,0].sum() + use_obj["array"][:,1,:,0].sum() - tradmar_obj["array"][:,1,:,:,0].sum()\
        +trade_obj["array"][:,0,1:,0].sum() +suppmar_obj["array"][:,:,0,1:].sum()
                
use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,:,0].sum()+suppmar_obj["array"][:,:,0,:].sum()  \
        + trade_obj["array"][:,0,0,1:].sum()+suppmar_obj["array"][:,:,1:,0].sum()  
#################################

##TEST

i=0
            # Use at delivered prices (including margins)
use_dp = pd.DataFrame(use_obj["array"][:,0,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
tradmar = pd.DataFrame(tradmar_obj["array"][:,0,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
margin = pd.DataFrame(pd.concat([tradmar, suppmar], axis=1)).fillna(0)
margin["Sup_pr"]=suppmar.div(suppmar.sum(axis=0)).fillna(0)
margin = margin.fillna(0)
            # Use at basic prices
use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows")
use_dp_sp_45_47=(use_dp_tr*suppmar_obj["array"][0,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
use_dp_sp_49_53=(use_dp_tr*suppmar_obj["array"][1,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
use_bp = use_dp - use_dp_tr
use_bp.loc["C_45_47"]=use_dp.loc["C_45_47"]+use_dp_sp_45_47
use_bp.loc["C_49_53"]=use_dp.loc["C_49_53"]+use_dp_sp_49_53
            
own_reg_share = (trade_obj["array"][:,0,i,i] / trade_obj["array"][:,0,:,i].sum(axis = 1))
u = np.matrix(use_bp)
use_bp= u - np.multiply(u, np.matrix(own_reg_share).transpose())
use_bp= pd.DataFrame(use_bp, columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 

             # Domestic export: flow from i to all other than i
exp_dom=pd.DataFrame(np.delete(trade_obj["array"][:,0,i,:], i, axis=1).sum(axis = 1), columns=["EXP"], index=trade_obj["sets"][0]["dim_desc"])
exp_dom.loc["C_45_47"]=exp_dom.loc["C_45_47"]+np.delete(suppmar_obj["array"][0,:,:,i], i, axis=1).sum()
exp_dom.loc["C_49_53"]=exp_dom.loc["C_49_53"]+np.delete(suppmar_obj["array"][1,:,:,i], i, axis=1).sum()
use_bp["Exp_dom"] = exp_dom
use_bp["Exp"] = 0
use_bp["IVENTORIES"]=0

trade_obj["array"][:,0,0,:].sum(axis=1)
suppmar_obj["array"][0,:,1:,].sum()

importlib.reload(ho)
u_io = ho.build_io(reg_supp.tables["Uusimaa"], reg_use.tables["Uusimaa"])
u_io.table

reg_io.tables["Uusimaa"].table

reg_supp.tables.keys()
reg_use.tables["Uusimaa"].table[[("Total_output", reg_use.tables["Uusimaa"].dims["FINAL"].values())]]
reg_use.tables["Uusimaa"].table

reg_use.tables["Uusimaa"].dims["FINAL"]
reg_use.tables["Uusimaa"].Ud



pd.DataFrame(use_obj["array"][:,0,:,0])[30:33]

# Domestic national: 
make_obj["array"][:,:,:].sum()
#equal to 
#equal to 
use_obj["array"][:,0,:,:].sum() - tradmar_obj["array"][:,0,:,:,:].sum() + suppmar_obj["array"][:,:,:,:].sum()

#Imports National:
use_obj["array"][:,1,:,:].sum()-tradmar_obj["array"][:,1,:,:,:].sum()


#Total national:
#trade_obj["array"][:,1,:,:].sum()+use_obj["array"][:,1,33,:].sum()=use_obj["array"][:,1,:,:].sum()
make_obj["array"][:,:,:].sum() + use_obj["array"][:,1,:,:].sum()-tradmar_obj["array"][:,1,:,:,:].sum()
#equal to 
use_obj["array"][:,:,:,:].sum() - tradmar_obj["array"][:,:,:,:,:].sum() + suppmar_obj["array"][:,:,:,:].sum()

# domestic uusimaa: make+regional import=use-trad_mar+sup_mar+regional export
use_obj["array"][:,0,:,0].sum() + suppmar_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,0,:,:,0].sum() + trade_obj["array"][:,0,0,1:].sum() 
#equal to 
make_obj["array"][:,:,0].sum() + trade_obj["array"][:,0,1:,0].sum() 

# total uusimaa
use_obj["array"][:,:,:,0].sum() + suppmar_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,:,0].sum()+trade_obj["array"][:,0,0,1:].sum() 
#equal to 
make_obj["array"][:,:,0].sum() + trade_obj["array"][:,0,1:,0].sum() + use_obj["array"][:,1,:,0].sum() - tradmar_obj["array"][:,1,:,:,0].sum()

suppmar_obj["array"][:,:,:,0].sum()=-suppmar_obj["array"][:,:,:,1:].sum()+suppmar_obj["array"][:,:,:,:].sum()
suppmar_obj["array"][:,:,0,:].sum()+suppmar_obj["array"][:,:,1:,:].sum()

suppmar_obj["array"][:,:,1:,:].sum()-suppmar_obj["array"][:,:,:,1:].sum()





#TEST!!!!!!!!!!!
use_obj["array"][:,:,:,0].sum() + suppmar_obj["array"][:,:,0,:].sum()- tradmar_obj["array"][:,:,:,:,0].sum()+trade_obj["array"][:,0,0,1:].sum()+suppmar_obj["array"][:,:,1:,:].sum()-suppmar_obj["array"][:,:,:,1:].sum()
#equal to 
make_obj["array"][:,:,0].sum() + trade_obj["array"][:,0,1:,0].sum() + use_obj["array"][:,1,:,0].sum() - tradmar_obj["array"][:,1,:,:,0].sum()

#suppmar_obj["array"][:,:,:,0].sum()=suppmar_obj["array"][:,:,0,:].sum()-suppmar_obj["array"][:,:,0,1:].sum()+suppmar_obj["array"][:,:,1:,0].sum()







#FINAL
#########################################################
#########################################################

#Solution 1:
#V_1
make_obj["array"][:,:,0].sum() + use_obj["array"][:,1,:,0].sum() - tradmar_obj["array"][:,1,:,:,0].sum()\
        +trade_obj["array"][:,0,1:,0].sum() +suppmar_obj["array"][:,:,0,1:].sum()
                
use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,0,0].sum()+suppmar_obj["array"][:,0,0,:].sum() \
        + trade_obj["array"][:,0,0,1:].sum()+suppmar_obj["array"][:,:,1:,0].sum()  

#tradmar_obj["array"][:,:,:,:,0].sum()-tradmar_obj["array"][:,:,:,0,0].sum()=tradmar_obj["array"][:,:,:,1:,0].sum()
#suppmar_obj["array"][:,:,0,:].sum() - suppmar_obj["array"][:,0,0,:].sum() =suppmar_obj["array"][:,1:,0,:].sum() 

#V_2
make_obj["array"][:,:,0].sum() + use_obj["array"][:,1,:,0].sum() - tradmar_obj["array"][:,1,:,:,0].sum()\
        +trade_obj["array"][:,0,1:,0].sum() +suppmar_obj["array"][:,:,0,1:].sum()+suppmar_obj["array"][:,1:,0,:].sum() -tradmar_obj["array"][:,:,:,1:,0].sum()
                
use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,:,0].sum()+suppmar_obj["array"][:,:,0,:].sum()  \
        + trade_obj["array"][:,0,0,1:].sum()+suppmar_obj["array"][:,:,1:,0].sum()  

trade_obj["array"][:,0,0,1:].sum(axis=1)
#tradmar_obj["array"][:,:,:,1:,0].sum()=suppmar_obj["array"][:,1:,0,:].sum()

#V_3 FINAL Total Uusimaa
make_obj["array"][:,:,0].sum() + use_obj["array"][:,1,:,0].sum() - tradmar_obj["array"][:,1,:,:,0].sum()\
        +trade_obj["array"][:,0,1:,0].sum() +suppmar_obj["array"][:,:,0,1:].sum()
                
use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,:,0].sum()+suppmar_obj["array"][:,:,0,:].sum()  \
        + trade_obj["array"][:,0,0,1:].sum()+suppmar_obj["array"][:,:,1:,0].sum()

suppmar_obj["array"][:,:,0,1:].sum()+suppmar_obj["array"][:,:,0,0].sum()=suppmar_obj["array"][:,:,0,:].sum()
suppmar_obj["array"][:,:,0,:].sum()-suppmar_obj["array"][:,:,0,0].sum()

suppmar_obj["array"][:,:,1:,0].sum() +suppmar_obj["array"][:,:,1:,1:].sum()  =suppmar_obj["array"][:,:,1:,:].sum()
suppmar_obj["array"][:,:,1:,:].sum()-suppmar_obj["array"][:,:,1:,1:].sum()

#V_32 FINAL Total Uusimaa
make_obj["array"][:,:,0].sum() + use_obj["array"][:,1,:,0].sum() - tradmar_obj["array"][:,1,:,:,0].sum()\
        +trade_obj["array"][:,0,1:,0].sum() +suppmar_obj["array"][:,:,0,:].sum()
                
use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,:,0].sum()+suppmar_obj["array"][:,:,0,:].sum()  \
        + trade_obj["array"][:,0,0,1:].sum()+suppmar_obj["array"][:,:,1:,:].sum()-suppmar_obj["array"][:,:,1:,1:].sum()+suppmar_obj["array"][:,:,0,0].sum()



#V_3 Domestic Uusimaa
make_obj["array"][:,:,0].sum() \
        +trade_obj["array"][:,0,1:,0].sum() +suppmar_obj["array"][:,:,0,1:].sum()
                
use_obj["array"][:,0,:,0].sum() - tradmar_obj["array"][:,0,:,:,0].sum()+suppmar_obj["array"][:,:,0,:].sum()  \
        + trade_obj["array"][:,0,0,1:].sum()+suppmar_obj["array"][:,:,1:,0].sum()  
########################################
make_obj["array"][:,:,0].sum() \
        +trade_obj["array"][:,0,1:,0].sum() +suppmar_obj["array"][:,:,0,1:].sum()
                
use_obj["array"][:,0,:,0].sum() - tradmar_obj["array"][:,0,:,:,0].sum()+suppmar_obj["array"][:,:,0,:].sum()  \
        + trade_obj["array"][:,0,0,1:].sum()+suppmar_obj["array"][:,:,1:,0].sum()  

suppmar_obj["array"][:,:,0,1:].sum()-suppmar_obj["array"][:,:,1:,0].sum()-suppmar_obj["array"][:,:,0,:].sum()+tradmar_obj["array"][:,0,:,:,0].sum()
trade_obj["array"][:,0,1:,0].sum()-trade_obj["array"][:,0,0,1:].sum()
trade_obj["array"][:,0,0,1:].sum()+trade_obj["array"][:,0,0,0].sum()=trade_obj["array"][:,0,0,:].sum()
trade_obj["array"][:,0,0,1:].sum()+trade_obj["array"][:,0,1:,1:].sum()=trade_obj["array"][:,0,:,1:].sum()

-trade_obj["array"][:,0,:,1:].sum()+trade_obj["array"][:,0,1:,1:].sum()+trade_obj["array"][:,0,1:,0].sum()
-trade_obj["array"][:,0,0,1:].sum()+trade_obj["array"][:,0,1:,0].sum()
#suppmar_obj["array"][:,:,0,1:].sum()+suppmar_obj["array"][:,:,0,0].sum()=suppmar_obj["array"][:,:,0,:].sum()
#suppmar_obj["array"][:,:,1:,0].sum()+suppmar_obj["array"][:,:,1:,1:].sum()=suppmar_obj["array"][:,:,1:,:].sum()

#V_4
make_obj["array"][:,:,0].sum() + use_obj["array"][:,1,:,0].sum() - tradmar_obj["array"][:,1,:,:,0].sum()\
        +trade_obj["array"][:,0,1:,0].sum() +suppmar_obj["array"][:,1:,0,:].sum()+suppmar_obj["array"][:,0,0,:].sum()-suppmar_obj["array"][:,:,0,0].sum()
                
use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,:,0].sum()+suppmar_obj["array"][:,:,0,:].sum()  \
        + trade_obj["array"][:,0,0,1:].sum()+suppmar_obj["array"][:,0,1:,:].sum()+suppmar_obj["array"][:,1:,1:,:].sum() -suppmar_obj["array"][:,:,1:,1:].sum()  

suppmar_obj["array"][:,1:,1:,:].sum() -suppmar_obj["array"][:,:,1:,1:].sum()-suppmar_obj["array"][:,0,0,:].sum()+suppmar_obj["array"][:,:,0,:].sum()-suppmar_obj["array"][:,:,0,1:].sum()

use_obj["array"][:,0,:,0].sum().columns()
#Solution 2:

suppmar_obj["array"][:,:,0,:].sum()
tradmar_obj["array"][:,0,:,:,0].sum()+tradmar_obj["array"][:,1,:,:,0].sum()

suppmar_obj["array"][:,:,:,:].sum()
tradmar_obj["array"][:,:,:,:,:].sum()

suppmar_obj["array"][:,:,0,:].sum()
tradmar_obj["array"][:,0,:,:,0].sum()


trade_obj["array"][:,0,:,:].sum() 
use_obj["array"][:,0,:,:].sum() - tradmar_obj["array"][:,0,:,:,:].sum() 

trade_obj["array"][:,0,:,0].sum() 
use_obj["array"][:,0,:,0].sum() - tradmar_obj["array"][:,0,:,:,0].sum() 

trade_obj["array"][:,1,:,0].sum() 
use_obj["array"][:,1,:,0].sum() - tradmar_obj["array"][:,1,:,:,0].sum() 

trade_obj["array"][:,:,:,0].sum() + tradmar_obj["array"][:,:,:,:,0].sum()  - suppmar_obj["array"][:,:,0,:].sum()
use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,:,0].sum() + tradmar_obj["array"][:,:,:,:,0].sum()  - suppmar_obj["array"][:,:,0,:].sum()

trade_obj["array"][:,:,:,0].sum()  - suppmar_obj["array"][:,:,0,:].sum()
use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,:,0].sum()  - suppmar_obj["array"][:,:,0,:].sum()

trade_obj["array"][:,0,:,0].sum() + trade_obj["array"][:,1,:,0].sum() - suppmar_obj["array"][:,:,0,:].sum()
use_obj["array"][:,0,:,0].sum() - tradmar_obj["array"][:,0,:,:,0].sum() +use_obj["array"][:,1,:,0].sum() - tradmar_obj["array"][:,1,:,:,0].sum() - suppmar_obj["array"][:,:,0,:].sum()

tradmar_obj["array"][:,:,:,:,0].sum()
suppmar_obj["array"][:,:,0,:].sum() 

tradmar_obj["array"][:,:,:,:,0].sum()
suppmar_obj["array"][:,:,0,:].sum ()

tradmar_obj["array"][:,:,:,0,0].sum()
suppmar_obj["array"][:,0,0,:].sum()

tradmar_obj["array"][:,:,:,0,1:].sum()
suppmar_obj["array"][:,0,1:,:].sum()

tradmar_obj["array"][:,:,:,1:,0].sum()
suppmar_obj["array"][:,1:,0,:].sum()

use_obj["array"][:,:,:,0].sum(axis=(1,2))-tradmar_obj["array"][:,:,:,:,0].sum(axis=(1,2,3))
trade_obj["array"][:,:,:,0].sum(axis=(1,2))

m=0
n=0
m1=0
n1=0
for i in range(0,19):
        m=m+np.delete(trade_obj["array"][:,0,i,:], i, axis=1).sum()
        n=n+np.delete(trade_obj["array"][:,0,:,i], i, axis=1).sum()
        m1=m1+tradmar_obj["array"][:,:,:,i,i].sum()
        n1=n1+suppmar_obj["array"][:,i,i,:].sum() 

m
n
m1
n1

trade_obj["array"][:,0,:,1:].sum()
trade_obj["array"][:,0,1:,:].sum()

pd.DataFrame(va_labour_obj["coeff_name"].strip(): va_labour_obj["array"].sum(axis = 1)[:,0])

use_obj["array"][:,:,:,:].sum() - tradmar_obj["array"][:,:,:,:,:].sum() + suppmar_obj["array"][:,:,:,:].sum() 
####
use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,0,0].sum()+suppmar_obj["array"][:,0,0,:].sum() \
        + trade_obj["array"][:,0,0,1:].sum()+suppmar_obj["array"][:,:,1:,0].sum()\
        - tradmar_obj["array"][:,:,:,1:,0].sum()+suppmar_obj["array"][:,1:,0,:].sum() 

make_obj["array"][:,:,0].sum() + trade_obj["array"][:,0,1:,0].sum() +suppmar_obj["array"][:,:,0,1:].sum()\
        +use_obj["array"][:,1,:,0].sum() - tradmar_obj["array"][:,1,:,:,0].sum()+ tradmar_obj["array"][:,:,:,0,1:].sum() - suppmar_obj["array"][:,0,1:,:].sum()

####
use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,0,0].sum()+suppmar_obj["array"][:,0,0,:].sum() \
        + trade_obj["array"][:,0,0,1:].sum()+suppmar_obj["array"][:,:,1:,0].sum()\
        -tradmar_obj["array"][:,:,:,0,1:].sum() + suppmar_obj["array"][:,0,1:,:].sum()

make_obj["array"][:,:,0].sum() + use_obj["array"][:,1,:,0].sum() - tradmar_obj["array"][:,1,:,:,0].sum()\
        + trade_obj["array"][:,0,1:,0].sum() +suppmar_obj["array"][:,:,0,1:].sum()\
        - tradmar_obj["array"][:,:,:,1:,0].sum()+suppmar_obj["array"][:,1:,0,:].sum()

#suppmar_obj["array"][:,0,0,:].sum()=suppmar_obj["array"][:,0,0,0].sum()+suppmar_obj["array"][:,0,0,1:].sum()

use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,0,0].sum()+suppmar_obj["array"][:,0,0,0].sum()\
        + trade_obj["array"][:,0,0,1:].sum()+suppmar_obj["array"][:,:,1:,0].sum()\
        -tradmar_obj["array"][:,:,:,0,1:].sum() + suppmar_obj["array"][:,0,1:,:].sum()

make_obj["array"][:,:,0].sum() + use_obj["array"][:,1,:,0].sum() - tradmar_obj["array"][:,1,:,:,0].sum()\
        + trade_obj["array"][:,0,1:,0].sum() +suppmar_obj["array"][:,:,0,1:].sum()\
        - tradmar_obj["array"][:,:,:,1:,0].sum()+suppmar_obj["array"][:,1:,0,:].sum()\
              -  suppmar_obj["array"][:,0,0,1:].sum()

#suppmar_obj["array"][:,0,1:,:].sum()=suppmar_obj["array"][:,0,1:,0].sum()+suppmar_obj["array"][:,0,1:,1:].sum()
use_obj["array"][:,0,:,0].sum() - tradmar_obj["array"][:,0,:,0,0].sum()+suppmar_obj["array"][:,0,0,0].sum()    
use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,0,0].sum()+suppmar_obj["array"][:,0,0,0].sum()\
        + trade_obj["array"][:,0,0,1:].sum()+suppmar_obj["array"][:,:,1:,0].sum()\
        -tradmar_obj["array"][:,:,:,0,1:].sum() + suppmar_obj["array"][:,0,1:,0].sum()

make_obj["array"][:,:,0].sum() + use_obj["array"][:,1,:,0].sum() - tradmar_obj["array"][:,1,:,:,0].sum()\
        + trade_obj["array"][:,0,1:,0].sum() +suppmar_obj["array"][:,:,0,1:].sum()\
        - tradmar_obj["array"][:,:,:,1:,0].sum()+suppmar_obj["array"][:,1:,0,:].sum()\
              -  suppmar_obj["array"][:,0,0,1:].sum()-suppmar_obj["array"][:,0,1:,1:].sum()

#suppmar_obj["array"][:,:,1:,0].sum()=suppmar_obj["array"][:,0,1:,0].sum()+suppmar_obj["array"][:,1:,1:,0].sum()

use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,0,0].sum()+suppmar_obj["array"][:,0,0,0].sum()\
        + trade_obj["array"][:,0,0,1:].sum()+suppmar_obj["array"][:,0,1:,0].sum()
        

make_obj["array"][:,:,0].sum() + use_obj["array"][:,1,:,0].sum() - tradmar_obj["array"][:,1,:,:,0].sum()\
        + trade_obj["array"][:,0,1:,0].sum() +suppmar_obj["array"][:,1:,0,1:].sum()

# Domestic national: 
make_obj["array"][:,:,:].sum()
#equal to 
use_obj["array"][:,0,:,:].sum() - tradmar_obj["array"][:,0,:,:,:].sum() + suppmar_obj["array"][:,:,:,:].sum()



#SOME EQUALITIES
#tradmar_obj["array"][:,:,:,:,0].sum() = suppmar_obj["array"][:,:,0,:].sum()
# suppmar_obj["array"][:,:,0,1:].sum()+suppmar_obj["array"][:,:,0,0].sum()=suppmar_obj["array"][:,:,0,:].sum()
#minus
# suppmar_obj["array"][:,:,1:,0].sum()+suppmar_obj["array"][:,:,0,0].sum()=suppmar_obj["array"][:,:,:,0].sum()
# suppmar_obj["array"][:,:,0,1:].sum()-suppmar_obj["array"][:,:,1:,0].sum()=suppmar_obj["array"][:,:,0,:].sum()-suppmar_obj["array"][:,:,:,0].sum()
# suppmar_obj["array"][:,:,0,1:].sum()-suppmar_obj["array"][:,:,1:,0].sum()=suppmar_obj["array"][:,:,0,:].sum()
#suppmar_obj["array"][:,:,:,0].sum()=suppmar_obj["array"][:,:,0,:].sum()-suppmar_obj["array"][:,:,0,1:].sum()+suppmar_obj["array"][:,:,1:,0].sum()

trade_obj["array"][:,0,:,:].sum() 
use_obj["array"][:,0,:,:].sum() - tradmar_obj["array"][:,0,:,:,:].sum() 

trade_obj["array"][:,0,:,0].sum() 

use_obj["array"][:,0,:,0].sum() - tradmar_obj["array"][:,0,:,:,0].sum() 
make_obj["array"][:,:,0].sum() 

trade_obj["array"][:,1,:,0].sum() 
use_obj["array"][:,1,:,0].sum() - tradmar_obj["array"][:,1,:,:,0].sum() 

trade_obj["array"][:,:,:,0].sum() + tradmar_obj["array"][:,:,:,:,0].sum()  - suppmar_obj["array"][:,:,0,:].sum()
use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,:,0].sum() + tradmar_obj["array"][:,:,:,:,0].sum()  - suppmar_obj["array"][:,:,0,:].sum()

trade_obj["array"][:,0,:,0].sum() 
use_obj["array"][:,0,:,0].sum() - tradmar_obj["array"][:,0,:,:,0].sum() 

trade_obj["array"][:,:,:,0].sum() + suppmar_obj["array"][:,:,:,0].sum()
use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,:,0].sum()  + suppmar_obj["array"][:,:,0,:].sum()


tradmar_obj["array"][:,:,:,:,0].sum()
suppmar_obj["array"][:,:,0,:].sum() 

tradmar_obj["array"][:,0,:,:,:].sum()
suppmar_obj["array"][:,:,:,0].sum() 

tradmar_obj["array"][:,:,:,:,0].sum()
suppmar_obj["array"][:,:,0,:].sum ()

tradmar_obj["array"][:,:,:,0,0].sum()
suppmar_obj["array"][:,0,0,:].sum()

tradmar_obj["array"][:,:,:,0,1:].sum()
suppmar_obj["array"][:,0,1:,:].sum()

tradmar_obj["array"][:,:,:,1:,0].sum()
suppmar_obj["array"][:,1:,0,:].sum()

use_obj["array"][:,:,:,:].sum()-tradmar_obj["array"][:,:,:,:,:].sum()
trade_obj["array"][:,:,:,:].sum()

make_obj["array"][:,:,:].sum()
trade_obj["array"][:,0,:,:].sum()+suppmar_obj["array"][:,:,:,:].sum()


#tradmar_obj["array"][:,:,:,1:,0].sum()=tradmar_obj["array"][:,:,:,1:,0].sum()

########################################

# regional tables
importlib.reload(ho)
reg_supp = ho.regSupplyTables(make_di,make_drp, trade_obj, use_obj, tradmar_obj)
reg_use = ho.regUseTables(use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj)

#######################################################################################################################################################################################
#TEST OF USE_PUR(IND)+GVA=OUTPUT
s=np.zeros([1,30])
for i in range(19):
        s=s+va_labour_obj["array"][:,:,i].sum(axis=1) +va_capital_obj["array"][:,i] +va_land_obj["array"][:,i] + prodtaxes_obj["array"][:,i]
s
#national
s.sum()+ tradmar_obj["array"][:,:,:,:,:].sum()- suppmar_obj["array"][:,:,:,:].sum() + taxes_obj["array"][:,:,0:30,:].sum()
make_obj["array"][:,:,:].sum()

#Uusimaa
m=np.zeros([1,30])
gva=np.zeros([1,30])
gva=va_labour_obj["array"][:,:,0].sum(axis=1) +va_capital_obj["array"][:,0] +va_land_obj["array"][:,0] + prodtaxes_obj["array"][:,0]
m=gva+taxes_obj["array"][:,:,0:30,0].sum(axis=(0,1))+use_obj["array"][:,:,0:30,0].sum(axis=(0,1))
make_obj["array"][:,:,0].sum(axis=0)+stocks_obj["array"][:,0]


m
make_obj["array"][:,:,0].sum(axis=0)

m=np.zeros([1,30])
gva=np.zeros([1,30])
for i in range(19):
        u=va_labour_obj["array"][:,:,i].sum(axis=1) +va_capital_obj["array"][:,i] +va_land_obj["array"][:,i] + prodtaxes_obj["array"][:,i]
        m=m+u+taxes_obj["array"][:,:,0:30,i].sum(axis=(0,1))+use_obj["array"][:,:,0:30,i].sum(axis=(0,1))
        gva=gva+u
m-make_obj["array"][:,:,:].sum(axis=(0,2))
m
taxes_obj["array"][:,:,0:30,:].sum(axis=(0,1,3))
use_obj["array"][:,:,0:30,:].sum(axis=(0,1,3))
make_obj["array"][:,:,:].sum(axis=(0,2))


#######################################################################################################################################################################################
# regional tables

importlib.reload(ho)

reg_supp = ho.regSupplyTables(make_obj, trade_obj)
reg_use = ho.regUseTables(use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj)

reg_supp.tables["Uusimaa"].table
reg_use.tables["Uusimaa"].table

reg_use.tables["Uusimaa"].Umext

u_io = ho.build_io(reg_supp.tables["Uusimaa"], reg_use.tables["Uusimaa"])
u_io.table

(reg_use.tables["Uusimaa"].U_dom - reg_use.tables["Uusimaa"].U_dom_own).sum()
np.multiply(reg_use.tables["Uusimaa"].Y_dom, np.matrix(reg_use.tables["Uusimaa"].own_reg_share).transpose())
np.multiply(reg_use.tables["Uusimaa"].U_dom, reg_use.tables["Uusimaa"].own_reg_share)

m = np.concatenate([(reg_use.tables["Uusimaa"].U_dom - reg_use.tables["Uusimaa"].U_dom_own).sum(axis = 1), (reg_use.tables["Uusimaa"].U - reg_use.tables["Uusimaa"].U_dom).sum(axis = 1)], axis =1).transpose()
pd.DataFrame(m)





(reg_use.tables["Uusimaa"].U_dom - reg_use.tables["Uusimaa"].U_dom_own).sum()
np.multiply(reg_use.tables["Uusimaa"].Y_dom, np.matrix(reg_use.tables["Uusimaa"].own_reg_share).transpose())
np.multiply(reg_use.tables["Uusimaa"].U_dom, reg_use.tables["Uusimaa"].own_reg_share)

m = np.concatenate([(reg_use.tables["Uusimaa"].U_dom - reg_use.tables["Uusimaa"].U_dom_own).sum(axis = 1), (reg_use.tables["Uusimaa"].U - reg_use.tables["Uusimaa"].U_dom).sum(axis = 1)], axis =1).transpose()
pd.DataFrame(m)

x1 = np.matrix(np.arange(9.0).reshape((3, 3)))


x2 = np.matrix([0.5,1,2]).transpose()
np.multiply(x1, x2)

range(len(reg_use.tables["Uusimaa"].table.columns)) - range(0,30)


# Write to excel
reg_supp.to_excel(file = "outdata/test_supp2014.xlsx")
reg_use.to_excel(file = "outdata/test_use2014.xlsx")

# use_obj["array"][:,0,0,0]

"""  OLD CALCULATIONS 

# New supply
u_make = pd.DataFrame(make_obj["array"][:,:,0], index=trade_obj["sets"][0]["dim_desc"])
u_imp_dom = pd.DataFrame(trade_obj["array"][:,0,1:,0].sum(axis = 1), columns = ["Imports_domestic"], index=trade_obj["sets"][0]["dim_desc"])
u_imp_ext = pd.DataFrame(trade_obj["array"][:,1,:,0].sum(axis = 1), columns = ["Imports_external"], index=trade_obj["sets"][0]["dim_desc"])
u_imp = pd.concat([u_imp_dom, u_imp_ext], axis=1)

su = ho.supplyTable(u_make, u_imp)






reg_use.tables["Uusimaa"].table
reg_supp.tables["Uusimaa"].table




u_use = pd.DataFrame(use_obj["array"][:,:,:,0].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"])
u_suppmar = pd.DataFrame(suppmar_obj["array"][:,:,:,0].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
u_tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,0].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
u_margin = pd.DataFrame(pd.concat([u_tradmar, u_suppmar], axis=1)).fillna(0)
u_margin["Margins"] = u_margin["Trade_margin"] -u_margin["Suppy_margin"]
u_use_bp = u_use - u_use.div(u_use.sum(axis=1), axis = "rows").mul(u_margin["Margins"], axis = "rows")
u_exp_dom = pd.DataFrame(trade_obj["array"][:,0,0,1:].sum(axis = 1), columns=["Export_domestic"], index = tradmar_obj["sets"][0]["dim_desc"])

pd.DataFrame(np.delete(trade_obj["array"][:,0,0,:], 0, axis=1).sum(axis = 1), columns=["Export_domestic"], index = tradmar_obj["sets"][0]["dim_desc"])

u_use.sum(axis=1)
u_use_bp.sum(axis=1)

su.table

"""  

# Whole economy

74585 - use_obj["array"][:,:,33,:].sum() 



use_obj["array"][:,:,:,:].sum() + tradmar_obj["array"][:,:,:,:,:].sum() - suppmar_obj["array"][:,:,:,:].sum() \
+ taxes_obj["array"][:,:,:,:].sum() + prodtaxes_obj["array"][:,:].sum()

use_obj["array"][:,:,:,:].sum() - tradmar_obj["array"][:,:,:,:,:].sum()
trade_obj["array"][:,:,:,:].sum()
make_obj["array"][:,:,:].sum() - suppmar_obj["array"][:,:,:,:].sum() + trade_obj["array"][:,1,:,:].sum()

use_obj["array"][:,0,:,:].sum() - tradmar_obj["array"][:,0,:,:,:].sum()
trade_obj["array"][:,0,:,:].sum()
make_obj["array"][:,:,:].sum() - suppmar_obj["array"][:,:,:,:].sum() 

# domestic uusimaa



use_obj["array"][:,0,:,0].sum() + suppmar_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,0,:,:,0].sum() + trade_obj["array"][:,0,0,1:].sum() 
make_obj["array"][:,:,0].sum() + trade_obj["array"][:,0,1:,0].sum()

use_obj["array"][:,:,:,0].sum() + suppmar_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,:,0].sum() + trade_obj["array"][:,0,0,1:].sum() 
make_obj["array"][:,:,0].sum() + trade_obj["array"][:,0,1:,0].sum()+ trade_obj["array"][:,1,1:,0].sum()

trade_obj["array"][:,:,1:,0].sum()

use_obj["array"][:,0,:,0].sum(axis = 1) + suppmar_obj["array"][:,:,:,0].sum(axis = 1) - tradmar_obj["array"][:,0,:,:,0].sum(axis = 1) 
trade_obj["array"][:,0,:,0].sum()
trade_obj["array"][:,0,:,0].sum(axis = 1)
use_obj["array"][:,0,:,0].sum(axis = 1)- tradmar_obj["array"][:,0,:,:,0].sum(axis = (1,2))
use_obj["array"][:,0,:,0].sum()- tradmar_obj["array"][:,0,:,:,0].sum()

# total uusimaa
use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,:,0].sum() + suppmar_obj["array"][:,:,:,0].sum() + trade_obj["array"][:,0,0,1:].sum() 
make_obj["array"][:,:,:].sum() + trade_obj["array"][:,1,:,:].sum()

use_obj["array"][:,:,:,:].sum() - tradmar_obj["array"][:,:,:,:,:].sum() + suppmar_obj["array"][:,:,:,:].sum()

use_obj["array"][29,1,:,:].sum()

trade_obj["array"][:,0,0,0] / trade_obj["array"][:,0,:,0].sum(axis = 1)

use_obj["array"][:,:,:,:].sum() 
use_obj["array"][:,:,:,:].sum() - tradmar_obj["array"][:,:,:,:,:].sum() 
make_obj["array"][:,:,:].sum() + trade_obj["array"][:,1,:,:].sum()
trade_obj["array"][:,1,:,:].sum() + tradmar_obj["array"][:,1,:,:,:].sum() 

ss = 0
for i in range(19):
    ss= ss + np.delete(trade_obj["array"][:,0,:,i],i, axis = 1).sum()
ss

ss = 0
for i in range(19):
    ss= ss + trade_obj["array"][:,0,:,i].sum()
ss

make_obj["array"][:,:,:].sum() 
trade_obj["array"][:,1,:,:].sum() + tradmar_obj["array"][:,1,:,:,:].sum() 
use_obj["array"][:,1,:,:].sum() 
use_obj["array"][:,0,:,:].sum() 

suppmar_obj["array"][:,:,:,:].sum()
"""
make_obj["array"].shape
trade_obj["array"].shape
make_obj["array"][:,:,0].sum(axis = 1)
make_obj["array"][:,:,0].sum(axis = 1)
trade_obj["array"][:,1,:,0].sum(axis = 1) + trade_obj["array"][:,0,1:18,0].sum(axis = 1)
pd.DataFrame(trade_obj["array"][:,0,0,:])
trade_obj["array"][:,0,0,:].sum(axis = 1)
use_obj["array"][:,1,:,:].sum()
make_obj["array"][:,:,:].sum()
trade_obj["array"][:,:,:,:].sum()

suppmar_obj["array"][:,:,:,:].sum()
 
# whole economy
use_obj["array"][:,:,:,:].sum() - tradmar_obj["array"][:,:,:,:,:].sum()
trade_obj["array"][:,:,:,:].sum()
make_obj["array"][:,:,:].sum() - suppmar_obj["array"][:,:,:,:].sum() + trade_obj["array"][:,1,:,:].sum()


# Domestics
use_obj["array"][:,0,:,:].sum() - tradmar_obj["array"][:,0,:,:,:].sum()
make_obj["array"][:,:,:].sum() - suppmar_obj["array"][:,:,:,:].sum()
trade_obj["array"][:,0,:,:].sum()

tradmar_obj["array"][:,:,:,:].sum()
trade_obj["array"][:,:,:,:].sum()



make_obj["array"][:,:,0].sum() + trade_obj["array"][:,0,1:18,0].sum() + trade_obj["array"][:,1,:,0].sum() + suppmar_obj["array"][:,:,:,:1:18].sum()
use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,0,:,:,0].sum()

# Regional level
use_obj["array"][:,0,:,0].sum() - tradmar_obj["array"][:,0,:,:,0].sum()
trade_obj["array"][:,0,:,0].sum() 

make_obj["array"][:,:,0].sum() - suppmar_obj["array"][:,:,:,0].sum()
trade_obj["array"][:,0,0,:].sum() 

# Regional level with trade
use_obj["array"][:,0,:,0].sum() - tradmar_obj["array"][:,0,:,:,0].sum()
trade_obj["array"][:,0,:,0].sum() 

make_obj["array"][:,:,0].sum() - suppmar_obj["array"][:,:,:,0].sum()
trade_obj["array"][:,0,0,:].sum() 
trade_obj["array"][:,0,0,:].sum() - trade_obj["array"][:,0,0,1:18].sum() + trade_obj["array"][:,0,1:18, 0].sum()

trade_obj["array"][:,0,0,:].sum() - trade_obj["array"][:,0,:,0].sum() 

trade_obj["array"][:,0,0,1:18].sum() - trade_obj["array"][:,0,1:18,0].sum()

""" # domestic uusimaa
use_obj["array"][:,0,:,0].sum() + suppmar_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,0,:,:,0].sum() + trade_obj["array"][:,0,0,1:].sum() 

trade_obj["array"][:,0,0,1:].sum()  
make_obj["array"][:,:,0].sum() + trade_obj["array"][:,0,1:,0].sum()
make_obj["array"][:,:,:].sum() - suppmar_obj["array"][:,:,:,:].sum()
trade_obj["array"][:,0,0,0].sum() + trade_obj["array"][:,0,0,1:].sum() 

 """

# total uusimaa
use_obj["array"][:,:,:,0].sum() + suppmar_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,:,0].sum()  + trade_obj["array"][:,0,0,1:].sum() 
make_obj["array"][:,:,0].sum() + trade_obj["array"][:,0,1:,0].sum() + trade_obj["array"][:,1,:,0].sum()

trade_obj["array"][:,:,0,:].sum()


use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,:,0].sum()
trade_obj["array"][:,:,:,0].sum()

make_obj["array"][:,:,0].sum() - suppmar_obj["array"][:,:,:,0].sum() + trade_obj["array"][:,1,0,:].sum() - trade_obj["array"][:,0,0,1:].sum() + trade_obj["array"][:,0,1:,0].sum()
trade_obj["array"][:,:,0,:].sum()
make_obj["array"][:,:,0].sum() - suppmar_obj["array"][:,:,:,0].sum() - trade_obj["array"][:,:,0,1:].sum() + trade_obj["array"][:,:,1:,0].sum()

trade_obj["array"][:,:,:,0].sum() - trade_obj["array"][:,:,0,:].sum()  
trade_obj["array"][:,:,:,0].sum() - trade_obj["array"][:,:,0,0].sum() - trade_obj["array"][:,:,1:,0].sum() 


trade_obj["array"][:,:,1:18,0].sum() - trade_obj["array"][:,:,0,1:18].sum()

(use_obj["array"][:,1,:,:].sum() - tradmar_obj["array"][:,1,:,:].sum())
use_obj["array"][:,:,:,:].sum()

writer = pd.ExcelWriter('outdata/uusimaa.xlsx', engine='xlsxwriter')
pd.DataFrame(make_obj["array"][:,:,0]).to_excel(writer, sheet_name="make")
pd.DataFrame(trade_obj["array"][:,0,0,:]).to_excel(writer, sheet_name="trade")
writer.save()

"""
use_dp = pd.DataFrame(use_obj["array"][:,:,:,0].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
suppmar = pd.DataFrame(suppmar_obj["array"][:,:,0,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"]) 
tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,0].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
margin = pd.DataFrame(pd.concat([tradmar, suppmar], axis=1)).fillna(0)
margin["Sup_pr"]=suppmar.div(suppmar.sum(axis=0)).fillna(0)
margin = margin.fillna(0)
# Use at basic prices
use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows")
use_dp_sp_45_47=(use_dp_tr*suppmar_obj["array"][0,:,0,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,0,:].sum()).sum(axis=0)
use_dp_sp_49_53=(use_dp_tr*suppmar_obj["array"][1,:,0,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,0,:].sum()).sum(axis=0) 
use_bp = use_dp - use_dp_tr
use_bp.loc["C_45_47"]=use_dp.loc["C_45_47"]+use_dp_sp_45_47
use_bp.loc["C_49_53"]=use_dp.loc["C_49_53"]+use_dp_sp_49_53

suppmar_obj["array"][0,:,0,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,0,:].sum()).sum(axis=0)
use_dp_sp_45_47+use_dp_sp_49_53-use_dp_tr.sum(axis=0)
use_dp_tr.sum(axis=0)

             # Domestic export: flow from i to all other than i
exp_dom = np.delete(trade_obj["array"][:,0,i,:], i, axis=1).sum(axis = 1)
use_bp["Exp_dom"] = exp_dom
margin=0


#############################################
make_obj["array"][:,:,0].sum() \
        +trade_obj["array"][:,0,1:,0].sum() +suppmar_obj["array"][:,:,0,1:].sum()
                
use_obj["array"][:,0,:,0].sum() - tradmar_obj["array"][:,0,:,:,0].sum()+suppmar_obj["array"][:,:,0,:].sum()  \
        + trade_obj["array"][:,0,0,1:].sum()+suppmar_obj["array"][:,:,1:,0].sum()  

#############################################

i=0

#total
use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
margin = pd.DataFrame(pd.concat([tradmar, suppmar], axis=1)).fillna(0)
margin["Sup_pr"]=suppmar.div(suppmar.sum(axis=0)).fillna(0)
margin = margin.fillna(0)
# Use at basic prices
use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows")
use_dp_sp_45_47=(use_dp_tr*suppmar_obj["array"][0,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
use_dp_sp_49_53=(use_dp_tr*suppmar_obj["array"][1,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
use_bp = use_dp - use_dp_tr
use_bp.loc["C_45_47"]=use_dp.loc["C_45_47"]+use_dp_sp_45_47
use_bp.loc["C_49_53"]=use_dp.loc["C_49_53"]+use_dp_sp_49_53


             # Domestic export: flow from i to all other than i
exp_dom=pd.DataFrame(np.delete(trade_obj["array"][:,0,i,:], i, axis=1).sum(axis = 1), columns=["EXP"], index=trade_obj["sets"][0]["dim_desc"])
exp_dom.loc["C_45_47"]=exp_dom.loc["C_45_47"]+np.delete(suppmar_obj["array"][0,:,:,i], i, axis=1).sum()
exp_dom.loc["C_49_53"]=exp_dom.loc["C_49_53"]+np.delete(suppmar_obj["array"][1,:,:,i], i, axis=1).sum()
use_bp["Exp_dom"] = exp_dom

stocks=stocks_obj["array"][:,i]
s=pd.DataFrame(stocks)
stocks=s.transpose()
stocks.index=["Stocks"]
stocks.columns=make_obj["sets"][1]["dim_desc"]
make2 = pd.DataFrame(make_obj["array"][:,:,i], columns = make_obj["sets"][1]["dim_desc"], index = make_obj["sets"][0]["dim_desc"])
inv0= make2.div(make2.sum(axis=0), axis = "columns").mul(stocks.loc["Stocks"], axis = "columns")
inv=inv0.sum(axis=1)
use_bp["IVENTORIES"]=inv

use_bp_total=use_bp

##dom
##spread total
use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
margin = pd.DataFrame(pd.concat([tradmar, suppmar], axis=1)).fillna(0)
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
            
use_bp["Exp"] = use_bp_exp

            #Inventories

stocks=stocks_obj["array"][:,i]
s=pd.DataFrame(stocks)
stocks=s.transpose()
stocks.index=["Stocks"]
stocks.columns=make_obj["sets"][1]["dim_desc"]
make2 = pd.DataFrame(make_obj["array"][:,:,i], columns = make_obj["sets"][1]["dim_desc"], index = make_obj["sets"][0]["dim_desc"])
inv0= make2.div(make2.sum(axis=0), axis = "columns").mul(stocks.loc["Stocks"], axis = "columns")
inv=inv0.sum(axis=1)
use_bp["Exp_dom"] = 0

use_bp["IVENTORIES"]=inv
use_bp_dom=use_bp
      

###regions
use_dp = pd.DataFrame(use_obj["array"][:,:,:,i].sum(axis = 1), columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
tradmar = pd.DataFrame(tradmar_obj["array"][:,:,:,:,i].sum(axis = (1,2,3)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
margin = pd.DataFrame(pd.concat([tradmar, suppmar], axis=1)).fillna(0)
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
use_bp_d_r= use_bp
#regions
own_reg_share = (trade_obj["array"][:,0,i,i] / trade_obj["array"][:,0,:,i].sum(axis = 1))
u = np.matrix(use_bp)
use_bp= u - np.multiply(u, np.matrix(own_reg_share).transpose())
use_bp= pd.DataFrame(use_bp, columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 

             # Domestic export: flow from i to all other than i
exp_dom=pd.DataFrame(np.delete(trade_obj["array"][:,0,i,:], i, axis=1).sum(axis = 1), columns=["EXP"], index=trade_obj["sets"][0]["dim_desc"])
exp_dom.loc["C_45_47"]=exp_dom.loc["C_45_47"]+np.delete(suppmar_obj["array"][0,:,:,i], i, axis=1).sum()

exp_dom.loc["C_49_53"]=exp_dom.loc["C_49_53"]+np.delete(suppmar_obj["array"][1,:,:,i], i, axis=1).sum()
use_bp["Exp_dom"] = exp_dom
use_bp["Exp"] = 0
use_bp["IVENTORIES"]=0

suppmar_obj["array"][0,:,1:,i].sum()


diff= pd.DataFrame(np.multiply(u, np.matrix(own_reg_share).transpose()).sum(axis=1), columns=["Own"], index=use_obj["sets"][0]["dim_desc"]) 
diff["X"]=make2.sum(axis=1)
diff["T-IMP-X"]=use_bp_d_r.sum(axis=1)-diff["X"]
diff["X-Own"]=diff["X"]-diff["Own"]
diff["Exp_dom"]=exp_dom
diff["(X-Own)- Exp_dom"]=diff["X-Own"]-diff["Exp_dom"]


use_bp_reg=use_bp

#calc_use_bp_imp     

use_dp = pd.DataFrame(use_obj["array"][:,1,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
#suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
margin = pd.DataFrame(tradmar_obj["array"][:,1,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"]).fillna(0)
# Use at basic prices
            # Use at basic prices
use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows").fillna(0)
use_bp = use_dp - use_dp_tr

use_bp["Exp_dom"] = 0
use_bp["IVENTORIES"]=0

use_bp_imp=use_bp




##dom_total
use_dp = pd.DataFrame(use_obj["array"][:,0,:,i], columns=use_obj["sets"][2]["dim_desc"], index=use_obj["sets"][0]["dim_desc"]) 
            # Margins
suppmar = pd.DataFrame(suppmar_obj["array"][:,:,i,:].sum(axis = (1,2)), columns=["Suppy_margin"], index=suppmar_obj["sets"][0]["dim_desc"])
tradmar = pd.DataFrame(tradmar_obj["array"][:,0,:,:,i].sum(axis = (1,2)), columns=["Trade_margin"], index = tradmar_obj["sets"][0]["dim_desc"])
margin = pd.DataFrame(pd.concat([tradmar, suppmar], axis=1)).fillna(0)
margin["Sup_pr"]=suppmar.div(suppmar.sum(axis=0)).fillna(0)
margin = margin.fillna(0)
            # Use at basic prices
use_dp_tr=use_dp.div(use_dp.sum(axis=1), axis = "rows").mul(margin["Trade_margin"], axis = "rows")
use_dp_sp_45_47=(use_dp_tr*suppmar_obj["array"][0,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
use_dp_sp_49_53=(use_dp_tr*suppmar_obj["array"][1,:,i,:].sum(axis=(0,1))/suppmar_obj["array"][:,:,i,:].sum()).sum(axis=0)
use_bp = use_dp - use_dp_tr
use_bp.loc["C_45_47"]=use_dp.loc["C_45_47"]+use_dp_sp_45_47
use_bp.loc["C_49_53"]=use_dp.loc["C_49_53"]+use_dp_sp_49_53
            
use_bp_exp=use_bp["Exp"]
use_bp["Exp"] = use_bp_exp

            #Inventories

stocks=stocks_obj["array"][:,i]
s=pd.DataFrame(stocks)
stocks=s.transpose()
stocks.index=["Stocks"]
stocks.columns=make_obj["sets"][1]["dim_desc"]
make2 = pd.DataFrame(make_obj["array"][:,:,i], columns = make_obj["sets"][1]["dim_desc"], index = make_obj["sets"][0]["dim_desc"])
inv0= make2.div(make2.sum(axis=0), axis = "columns").mul(stocks.loc["Stocks"], axis = "columns")
inv=inv0.sum(axis=1)
use_bp["Exp_dom"] = 0
use_bp["IVENTORIES"]=inv
use_bp_dt=use_bp
      


use_bp_imp+use_bp_reg+use_bp_dom-use_bp_total
use_bp_dt-use_bp_imp-use_bp_reg

d=use_bp_reg+use_bp_dom
use_bp_reg2=use_bp_reg
use_bp_reg2["Exp_dom"]=0
use_bp_reg.sum(axis=1)+use_bp_dom.sum(axis=1)-make2.sum(axis=1)
use_bp_reg2.sum(axis=1)+use_bp_dom.sum(axis=1)-make2.sum(axis=1)

d.sum(axis=1)-make_obj["array"][:,:,0].sum(axis=1)
make_obj["array"][:,:,0].sum(axis=1)
use_bp_dom.sum(axis=1)-make_obj["array"][:,:,0].sum(axis=1)
