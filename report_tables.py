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

import importlib
importlib.reload(ho)

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

ho.to_long_table(reg_supp_fi).to_csv(outdataFolder + "/supp2014.csv", sep = ";", index = False)


#use Table - total
reg_use = ho.regUseTables(use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj, taxes_obj, make_obj, stocks_obj)
reg_use_fi = ho.translate_reg_tables(reg_use, "reg_use")
reg_use_fi.to_excel(file = outdataFolder + "/use2014.xlsx")

ho.to_long_table(reg_use_fi).to_csv(outdataFolder + "/use2014.csv", sep = ";", index = False)

#use Table - domestic
reg_use_dom = ho.regUseTab_dom(use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj, taxes_obj, make_obj, stocks_obj)
reg_use_dom_fi = ho.translate_reg_tables(reg_use_dom, "reg_use_dom")
reg_use_dom_fi.to_excel(file = outdataFolder + "/use_dom2014.xlsx")
reg_use_dom.to_excel(file = outdataFolder + "/use_dom2014_en.xlsx")
ho.to_long_table(reg_use_dom_fi).to_csv(outdataFolder + "/use_dom2014.csv", sep = ";", index = False)


#use Table - regional
reg_use_reg = ho.regUseTab_reg(use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj, taxes_obj, make_obj, stocks_obj)
reg_use_reg_fi = ho.translate_reg_tables(reg_use_reg, "reg_use_reg")
reg_use_reg_fi.to_excel(file = outdataFolder + "/use_reg2014.xlsx")

ho.to_long_table(reg_use_reg_fi).to_csv(outdataFolder + "/use_reg2014.csv", sep = ";", index = False)


#use Table - foreign imports
reg_use_imp = ho.regUseTab_imp(use_obj, trade_obj, tradmar_obj, suppmar_obj, va_labour_obj, va_capital_obj, va_land_obj, prodtaxes_obj, taxes_obj, make_obj, stocks_obj)
reg_use_imp_fi = ho.translate_reg_tables(reg_use_imp, "reg_use_imp")
reg_use_imp_fi.to_excel(file = outdataFolder + "/use_imp2014.xlsx")

ho.to_long_table(reg_use_imp_fi).to_csv(outdataFolder + "/use_imp2014.csv", sep = ";", index = False)


#I-O table domestic old
# reg_io = ho.regIOtables(reg_supp, reg_use)
# reg_io_fi = ho.translate_reg_tables(reg_io, "reg_io")
# reg_io_fi.to_excel(file = outdataFolder + "/io2014.xlsx")

#I-O table domestic
reg_io = ho.regIOtables2(reg_supp, reg_use)
reg_io_fi = ho.translate_reg_tables(reg_io, "reg_io")
reg_io_fi.to_excel(file = outdataFolder + "/io2014.xlsx")

ho.to_long_table(reg_io_fi).to_csv(outdataFolder + "/io2014.csv", sep = ";", index = False)

#I-O table regional
reg_io_reg = ho.regIOtables_reg(reg_supp, reg_use)
reg_io_reg_fi = ho.translate_reg_tables(reg_io_reg, "reg_io")
reg_io_reg_fi.to_excel(file = outdataFolder + "/io_reg2014.xlsx")

ho.to_long_table(reg_io_reg_fi).to_csv(outdataFolder + "/io_reg2014.csv", sep = ";", index = False)


#I-O table foreign imports
reg_io_imp = ho.regIOtables_imp(reg_supp, reg_use)
reg_io_imp_fi = ho.translate_reg_tables(reg_io_imp, "reg_io")
reg_io_imp_fi.to_excel(file = outdataFolder + "/io_imp2014.xlsx")

ho.to_long_table(reg_io_imp_fi).to_csv(outdataFolder + "/io_imp2014.csv", sep = ";", index = False)

reg_io_coef = ho.regIOtables_coef(reg_supp, reg_use)
reg_io_coef_fi = ho.translate_reg_tables(reg_io_coef, "reg_io")
reg_io_coef_fi.to_excel(file = outdataFolder + "/io_coef2014.xlsx")

ho.to_long_table(reg_io_coef_fi).to_csv(outdataFolder + "/io_coef2014.csv", sep = ";", index = False)


for row in range(0,19):
        for col in range(0,19):
                for com in range(0,2):
                        trade_obj["array"][com+16,0,row,col]=trade_obj["array"][com+16,0,row,col]+suppmar_obj["array"][com,row,col,:].sum()


for row in range(0,19):
        for col in range(0,19):
                s=np.zeros([30])
                for com in range(0,30):
                        s[com]=trade_obj["array"][com,:,row,col].sum()/(trade_obj["array"][com,:,:,col].sum(axis=(0,1))+0.000001)
                v=pd.DataFrame(np.diagflat(s))
                if col==0:
                        V=v
                else:
                        V=pd.concat([V,v], axis=1)
        if row==0:
                C_mat=V
        else:
                C_mat=pd.concat([C_mat,V], axis=0)
   
C_mat=np.matrix(C_mat)

reg=use_obj["sets"][3]["dim_desc"]
A_mat = np.matrix(np.zeros((570, 570)))
j=0
for i in reg:
        A_mat[j*30:(j+1)*30-1,j*30:(j+1)*30-1] = np.matrix(reg_io_coef.tables[i].At)[0:29,0:29]
        j=j+1
        
#Inverse_matrix=inverse(I-C*A)
Inv_mat=pd.DataFrame(np.linalg.inv(np.identity(570, dtype = None)-C_mat*A_mat))

#Inverse_matrix*C
#For details, see Chapter 3 in Miller & Blair, 2009, "Input-Output Analysis: Foundations And Extensions", 2nd Edition
Inv_mat_C=pd.DataFrame(np.linalg.inv(np.identity(570, dtype = None)-C_mat*A_mat)*C_mat)

com=use_obj["sets"][0]["dim_desc"]

list=[]

for i in reg:
        for j in com:
                k=i+"_"+j
                list.append(k)
        
Inv_mat_dat=pd.DataFrame(np.matrix(Inv_mat), index=[list], columns=list)
Inv_mat_C_dat=pd.DataFrame(np.matrix(Inv_mat_C), index=[list], columns=list)
writer = pd.ExcelWriter(outdataFolder + "/Inv_mat.xlsx", engine='xlsxwriter')
Inv_mat_dat.to_excel(writer, sheet_name = "Inverse matrix")
workbook  = writer.book
worksheet = writer.sheets["Inverse matrix"]
format = workbook.add_format()
format.set_align('center')
format.set_align('vcenter')
format.set_num_format('0.000')
format.set_text_wrap()
worksheet.set_column('A:UZ',21, format)
Inv_mat_C_dat.to_excel(writer, sheet_name = "Inv_mat_to_C")
worksheet = writer.sheets["Inv_mat_to_C"]
format = workbook.add_format()
format.set_align('center')
format.set_align('vcenter')
format.set_num_format('0.000')
format.set_text_wrap()
worksheet.set_column('A:UZ',21, format)
writer.save()