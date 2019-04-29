# -*- coding: utf-8 -*-
"""
Report regional input output tables

@author: jh

"""

import pandas as pd
import numpy as np
import har2output as ho
import os

# HARPY module by Centre of Policy Studies for writing data into Header Array (HAR) format.
# Available at https://github.com/GEMPACKsoftware/HARPY
import harpy
from harpy.har_file import HarFileObj

# import importlib
# importlib.reload(ho)

harFolder = "hardata"
termFolder = "TERM"
outdataFolder = "outdata"


# Read premod har-file that includes regionalized data
premod = harpy.HarFileObj.loadFromDisk(termFolder+"/premod.har")

#Read basedata30 where Exports from Imports Use Table is located
base30 = harpy.HarFileObj.loadFromDisk(harFolder+"/basedata30.har")


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
#Read Exports from Imports Use Table (re-exports) into use_e
use_e = base30.getHeaderArrayObj("4BAI")
for j in range(0,19):
    for i in range(0,30):
        use_obj["array"][i,1,33,j]=use_obj["array"][i,0,33,j]/(use_obj["array"][i,0,33,:].sum()+0.000001)*use_e["array"][i] 

# To write tranlate file template
# pd.DataFrame(reg_io.tables["Uusimaa"].table.index, columns=["index"]).to_csv("translate/reg_io_index.csv", index=False, sep=";", mode="x")
# pd.DataFrame(reg_io.tables["Uusimaa"].table.columns, columns=["columns"]).to_csv("translate/reg_io_columns.csv", index=False, sep=";", mode="x")


#Supply table
reg_supp = ho.regSupplyTables(make_obj, use_obj, tradmar_obj, suppmar_obj, trade_obj, stocks_obj)
reg_supp_fi = ho.translate_reg_tables(reg_supp, "reg_supp")
reg_supp_fi.to_excel(file = outdataFolder + "/supp2014.xlsx")

#use Table - total
reg_use = ho.regUseTables(use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj, taxes_obj, make_obj, stocks_obj)
reg_use_fi = ho.translate_reg_tables(reg_use, "reg_use")
reg_use_fi.to_excel(file = outdataFolder + "/use2014.xlsx")

#use Table - domestic
reg_use_dom = ho.regUseTab_dom(use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj, taxes_obj, make_obj, stocks_obj)
reg_use_dom_fi = ho.translate_reg_tables(reg_use_dom, "reg_use_dom")
reg_use_dom_fi.to_excel(file = outdataFolder + "/use_dom2014.xlsx")

#use Table - regional
reg_use_reg = ho.regUseTab_reg(use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj, taxes_obj, make_obj, stocks_obj)
reg_use_reg_fi = ho.translate_reg_tables(reg_use_reg, "reg_use_reg")
reg_use_reg_fi.to_excel(file = outdataFolder + "/use_reg2014.xlsx")

#use Table - foreign imports
reg_use_imp = ho.regUseTab_imp(use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj, taxes_obj, make_obj, stocks_obj)
reg_use_imp_fi = ho.translate_reg_tables(reg_use_imp, "reg_use_imp")
reg_use_imp.to_excel(file = outdataFolder + "/use_imp2014.xlsx")

#I-O table domestic
reg_io = ho.regIOtables(reg_supp, reg_use)
reg_io_fi = ho.translate_reg_tables(reg_io, "reg_io")
reg_io_fi.to_excel(file = outdataFolder + "/io2014.xlsx")

#I-O table domestic ver-2
reg_io2 = ho.regIOtables2(reg_supp, reg_use)
reg_io2.to_excel(file = outdataFolder + "/io_2_2014.xlsx")

#I-O table regional
reg_io_reg = ho.regIOtables_reg(reg_supp, reg_use)
reg_io_reg.to_excel(file = outdataFolder + "/io_reg2014.xlsx")

#I-O table foreign imports
reg_io_imp = ho.regIOtables_imp(reg_supp, reg_use)
reg_io_imp.to_excel(file = outdataFolder + "/io_imp2014.xlsx")

reg_io_coef = ho.regIOtables_coef(reg_supp, reg_use)
reg_io_coef.to_excel(file = outdataFolder + "/io_coef2014.xlsx")

