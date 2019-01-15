# -*- coding: utf-8 -*-
"""
Calculations for input-output tables

@author: jh

"""

import pickle
import pandas as pd
import numpy as np
import har2output as ho

import importlib
# importlib.reload(ho)

# import data

inter_folder = "interdata"
cleanData = pickle.load(open(inter_folder+"/cleanData.p", "rb" ))  
table_dims = pickle.load(open(inter_folder+"/table_dims.p", "rb" ))  




sup_tab = ho.supplyTable(make = cleanData["supplytable_BP"].loc[table_dims["COM"], table_dims["IND"]], \
                         use_imp = cleanData["supplytable_BP"].loc[:,"P7R_CIF"])

use_tab = ho.useTable(use = cleanData["usetable_BP"].loc[table_dims["COM"], table_dims["IND"]], \
                    final = cleanData["usetable_BP"].loc[table_dims["COM"], table_dims["finUse"]], \
                    va = cleanData["usetable_BP"].loc[table_dims["valAdd"], table_dims["IND"]])

use_imp_tab = ho.useTable(use = cleanData["usetable_Imp_BP"].loc[table_dims["COM"], table_dims["IND"]], \
                    final = cleanData["usetable_Imp_BP"].loc[table_dims["COM"], table_dims["finUse"]], \
                    va = cleanData["usetable_Imp_BP"].loc[table_dims["valAdd"], table_dims["IND"]])



# B = T * U = V * inv(diag(q)) * U
B = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * (use_tab.use - use_imp_tab.use)
# F = T * Y = V * inv(diag(q)) * Y
F = sup_tab.VT.transpose() * np.linalg.inv(np.diagflat(sup_tab.q)) * use_tab.final

io_tab = ho.ioTable(B = pd.DataFrame(B, index=table_dims["IND"], columns=table_dims["IND"]), \
                    F = pd.DataFrame(F, index=table_dims["IND"], columns=table_dims["finUse"]),\
                    W = cleanData["usetable_BP"].loc[table_dims["valAdd"], table_dims["IND"]])

writer = pd.ExcelWriter("outdata/test_io.xlsx", engine='xlsxwriter')
sup_tab.table.to_excel(writer, sheet_name = "supply")
use_tab.table.to_excel(writer, sheet_name = "use")
io_tab.table.to_excel(writer, sheet_name = "io")
writer.save()

