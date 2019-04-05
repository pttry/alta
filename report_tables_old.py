# -*- coding: utf-8 -*-
"""
Report regional input output tables

@author: jh

"""

import pandas as pd
import numpy as np
import har2output as ho
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




reg_supp = ho.regSupplyTables(make_obj, use_obj, tradmar_obj, trade_obj, )
reg_use = ho.regUseTables(use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj, taxes_obj)
reg_io = ho.regIOtables(reg_supp, reg_use)

# Write to excel
reg_supp.to_excel(file = "outdata/test_supp2014.xlsx")
reg_use.to_excel(file = "outdata/test_use2014.xlsx")
reg_io.to_excel(file = "outdata/test_io2014.xlsx")

importlib.reload(ho)
u_io = ho.build_io(reg_supp.tables["Uusimaa"], reg_use.tables["Uusimaa"])
u_io.table

reg_io.tables["Uusimaa"].table

reg_supp.tables.keys()
reg_use.tables["Uusimaa"].table[[("Total_output", reg_use.tables["Uusimaa"].dims["FINAL"].values())]]

s = 0
for i in reg_use.tables.keys():
        s = s + reg_use.tables[i].table.loc[["Output"]]["Sum"].sum()

s = 0
for i in reg_use.tables.keys():
        s = s + reg_use.tables[i].table.loc[["V1CAP", "V1LAB", "V1LND", "V1PTX"]]["I_02_03"].sum()


s = 0
for i in reg_supp.tables.keys():
        s = s + reg_supp.tables[i].table.loc[["Products_total"]]["Total_output"].sum()



reg_use.tables.keys()

reg_use.tables[0].table.loc[["V1CAP", "V1LAB", "V1LND", "V1PTX"]]["Sum"]
reg_use.tables["Uusimaa"].dims["FINAL"]
reg_use.tables["Uusimaa"].Ud



va_labour_obj["array"].sum(axis = 1)[:,:].sum() + va_capital_obj["array"][:,:].sum() + va_land_obj["array"][:,:].sum() + prodtaxes_obj["array"][:,:].sum()


pd.DataFrame(use_obj["array"][:,0,:,0])[30:33]

# Domestic national: 
make_obj["array"][:,:,:].sum()
#equal to 
trade_obj["array"][:,0,:,:].sum()
#equal to 
use_obj["array"][:,0,:,:].sum() - tradmar_obj["array"][:,0,:,:,:].sum() + suppmar_obj["array"][:,:,:,:].sum()

#Imports National:
use_obj["array"][:,1,:,:].sum()-tradmar_obj["array"][:,1,:,:,:].sum()


#Total national:
#trade_obj["array"][:,1,:,:].sum()+use_obj["array"][:,1,33,:].sum()=use_obj["array"][:,1,:,:].sum()
make_obj["array"][:,:,:].sum() + use_obj["array"][:,1,:,:].sum()-tradmar_obj["array"][:,1,:,:,:].sum()
#equal to 
use_obj["array"][:,:,:,:].sum() - tradmar_obj["array"][:,:,:,:,:].sum() + suppmar_obj["array"][:,:,:,:].sum()


#domestic uusimaa: VERSION1
use_obj["array"][:,0,:,0].sum() + suppmar_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,0,:,:,0].sum() + trade_obj["array"][:,0,0,1:].sum() 
#equal to 
make_obj["array"][:,:,0].sum() + trade_obj["array"][:,0,1:,0].sum() 

# total uusimaa
use_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,:,:,:,0].sum() + suppmar_obj["array"][:,:,:,0].sum() + trade_obj["array"][:,0,0,1:].sum() 
#equal to 
make_obj["array"][:,:,0].sum() + trade_obj["array"][:,0,1:,0].sum() + use_obj["array"][:,1,:,0].sum() - tradmar_obj["array"][:,1,:,:,0].sum()

#######################################

# regional tables
importlib.reload(ho)
reg_supp = ho.regSupplyTables(make_di,make_drp, trade_obj, use_obj, tradmar_obj)
reg_use = ho.regUseTables(use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj)

#######################################################################################################################################################################################
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
