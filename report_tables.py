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


import harpy

# HARPY module by Centre of Policy Studies for writing data into Header Array (HAR) format.
# Available at https://github.com/GEMPACKsoftware/HARPY
from harpy.har_file import HarFileObj

harFolder = "hardata"
termFolder = "TERM"


# Read premod har-file that includes regionalized data
premod = harpy.HarFileObj.loadFromDisk(termFolder+"/premod.har")

# objects from premod
make_obj = premod.getHeaderArrayObj("MAKE")
use_obj = premod.getHeaderArrayObj("BSMR")
va_labour_obj = premod.getHeaderArrayObj("1LAB")
va_capital_obj = premod.getHeaderArrayObj("1CAP")
va_land_obj = premod.getHeaderArrayObj("1LND")
trade_obj = premod.getHeaderArrayObj("TRAD")
tradmar_obj = premod.getHeaderArrayObj("TMAR")
suppmar_obj = premod.getHeaderArrayObj("MARS")


# regional tables
reg_use = ho.regUseTables(use_obj, va_labour_obj, va_capital_obj, va_land_obj)
reg_supp = ho.regSupplyTables(make_obj, use_obj)

u_make = pd.DataFrame(make_obj["array"][:,:,0], index=trade_obj["sets"][0]["dim_desc"])
u_imp_dom = pd.DataFrame(trade_obj["array"][:,0,1:,0].sum(axis = 1), columns = ["Imports_domestic"], index=trade_obj["sets"][0]["dim_desc"])
u_imp_ext = pd.DataFrame(trade_obj["array"][:,1,:,0].sum(axis = 1), columns = ["Imports_external"], index=trade_obj["sets"][0]["dim_desc"])
u_imp = pd.concat([u_imp_dom, u_imp_ext], axis=1)


importlib.reload(ho)

su = ho.supplyTable(u_make, u_imp)

su.table

trade_obj["sets"][0]["dim_desc"]
trade_obj.getNames
make_obj["array"][:,:,0].sum() + trade_obj["array"][:,0,1:,0].sum() + trade_obj["array"][:,1,:,0].sum()


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

# domestic uusimaa
use_obj["array"][:,0,:,0].sum() + suppmar_obj["array"][:,:,:,0].sum() - tradmar_obj["array"][:,0,:,:,0].sum() + trade_obj["array"][:,0,0,1:].sum() 
make_obj["array"][:,:,0].sum() + trade_obj["array"][:,0,1:,0].sum()

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



# Write to excel
reg_supp.to_excel(file = "outdata/test2014.xlsx")
reg_use.to_excel(file = "outdata/test_use2014.xlsx")