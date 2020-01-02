#%% [markdown]
# # Government accounts

#%%
# Import all necessary modules:

# Basic modules
import pandas as pd
import numpy  as np
import os
import re

# HARPY module by Centre of Policy Studies for writing data into Header Array (HAR) format.
# Available at https://github.com/GEMPACKsoftware/HARPY
from harpy.har_file import HarFileObj
from harpy.header_array import HeaderArrayObj as HAO

import dataGetterFunction as dgf
import harWriterFunction  as hwf
import mapperFunction as imf
import checkerFunctions as cfs


#%%
# Choose base year for data:
baseYear = 2014
# Raw data folder:
rawFolder = "rawdata"
# Folder for output HAR-files:
harFolder = "hardata"


#%%
# Read data from previous steps:
baseData = HarFileObj.loadFromDisk(harFolder+"/basedataNEW.har")

#%% [markdown]
# #### Read data entries from previous steps:

#%%
# Sets:
COM = baseData.getHeaderArrayObj("COM")["array"].tolist()
IND = baseData.getHeaderArrayObj("IND")["array"].tolist()
SRC = baseData.getHeaderArrayObj("SRC")["array"].tolist()
OCC = baseData.getHeaderArrayObj("OCC")["array"].tolist()
MAR = baseData.getHeaderArrayObj("MAR")["array"].tolist()
# HarFileObj leaves some trailing whitespaces to some entries (this may have changed in more recent versions). 
# Remove them with:
COM = [c.strip(' ') for c in COM]
IND = [i.strip(' ') for i in IND]
SRC = [s.strip(' ') for s in SRC]
OCC = [o.strip(' ') for o in OCC]
MAR = [m.strip(' ') for m in MAR]


#%%
# Read national accounts industries from capital data (81 industries)
capitalData = HarFileObj.loadFromDisk(harFolder+"/capital.har")
NIND = capitalData.getHeaderArrayObj("NIND")["array"].tolist()
NIND = [n.strip(' ') for n in NIND]


#%%
# Numerical data:

# Taxes and tariffs:
V1TAX_CSI= baseData.getHeaderArrayObj("1TAX")["array"].sum()
V2TAX_CS= pd.Series(baseData.getHeaderArrayObj("2TAX")["array"].sum(axis=1).sum(axis=0), index = IND)
V2TAX_CSI = V2TAX_CS.sum()
V3TAX = pd.DataFrame(baseData.getHeaderArrayObj("3TAX")["array"], index = COM, columns = SRC)
V3TAX_CS = V3TAX.sum().sum()
V4TAX = pd.Series(baseData.getHeaderArrayObj("4TAX")["array"], index = COM)
V4TAX_C = V4TAX.sum()
V5TAX = pd.DataFrame(baseData.getHeaderArrayObj("5TAX")["array"], index = COM, columns = SRC)
V5TAX_CS = V5TAX.sum().sum()
V6TAX = pd.DataFrame(baseData.getHeaderArrayObj("6TAX")["array"], index = COM, columns = SRC)
V6TAX_CS = V6TAX.sum().sum()
V0TAR = pd.Series(baseData.getHeaderArrayObj("0TAR")["array"], index = COM)
V0TAR_C = V0TAR.sum()
V1PTX = pd.Series(baseData.getHeaderArrayObj("1PTX")["array"], index = IND)
V1PTX_I = V1PTX.sum()
V0TAX_CSI = V1TAX_CSI + V2TAX_CSI + V3TAX_CS + V4TAX_C + V5TAX_CS + V0TAR_C + V1PTX_I

# Factor data:
V1LAB = pd.DataFrame(baseData.getHeaderArrayObj("1LAB")["array"], index = IND, columns = OCC)
V1LAB_O = V1LAB.sum(axis=1)
V1CAP = pd.Series(baseData.getHeaderArrayObj("1CAP")["array"], index = IND) # VAIHDA TÄHÄN: LUE CAPITAL.HARrista
V1LND = pd.Series(baseData.getHeaderArrayObj("1LND")["array"], index = IND)

# Basic and purchasers priced flows:
V2BAS_CS = pd.Series(baseData.getHeaderArrayObj("2BAS")["array"].sum(axis=1).sum(axis=0), index = IND)
V2MAR_CSM = baseData.getHeaderArrayObj("2MAR")["array"].sum(axis=1).sum(axis=0).sum(axis=1)
V2PUR_CS = V2BAS_CS + V2TAX_CS + V2MAR_CSM
V5BAS = pd.DataFrame(baseData.getHeaderArrayObj("5BAS")["array"], index = COM, columns = SRC)
V5MAR_CSM = baseData.getHeaderArrayObj("5MAR")["array"].sum()
V5MAR = baseData.getHeaderArrayObj("5MAR")["array"]

#%% [markdown]
# ## Step 1: Compile public sector data
# 
# * Annual national accounts: 012 - Sector accounts
# * Annual national accounts: 014 - General government's total revenue and -expenditure
# * Annual national accounts: 007 - Production and generation of income
# * Government finance: 002 - Taxes and tax-like payments
# * Annual national accounts: 016 - Gross fixed capital formation
# * Government finance: 001 - General gov't expenditure by function (=COFOG)
#%% [markdown]
# #### Sector accounts

#%%
# Specify data location:
urlDict = {
"Sector accounts": "kan/vtp/statfinpas_vtp_pxt_012_201800.px",
"Govt accounts" :"kan/vtp/statfinpas_vtp_pxt_014_201800.px"}
# 012 -- Sector accounts 1975-2017
# 014 -- General government's total revenue and -expenditure 1975-2017

# Perform query:
dgf.getData(urlDict, baseYear = baseYear, filters = {"Sektori": ["S13"]}, search = True, active=False)


#%%
# Read in data:
sectorData = {k: pd.read_csv(rawFolder+"/"+str(k)+"_Rawdata.csv",encoding="ISO-8859-1",na_values =".") for k in urlDict.keys()} 


#%%
# Clean data:
for i in sectorData:
    sectorData[i].fillna(0, inplace = True)
    sectorData[i].rename(columns = {"Sector:": "Sector"}, inplace = True) # NOTE STATFIN TYPO!
    for col in sectorData[i]:
        if col in ["Sector", "Transaction"]:
            sectorData[i][col] = sectorData[i][col].apply(lambda x: x.split(" ")[0])
        
        if col == "Information":
            sectorData[i].replace({"Current prices": "CP"}, inplace = True)   
# Include only current price values: 
sectorData["Govt accounts"] = sectorData["Govt accounts"][sectorData["Govt accounts"]["Information"] == "CP"].reset_index(drop=True)

#%% [markdown]
# #### Government expenditure by function

#%%
# Specify data location:
#urlDict = {"Expenditure":    "jul/jmete/statfin_jmete_pxt_001.px",
#           "Debt":           "jul/jali/statfin_jali_pxt_002.px",
#           "Deficit":        "jul/jali/statfin_jali_pxt_001.px"}
# 001 -- General goverment expenditures by function 1990-2016
# 002 -- General government debt, consolidated between sub-sectors 1975-2017
# 001 -- General government deficit and debt 1975-2017

# Perform query:
#dgf.getData(urlDict, baseYear = baseYear)


#%%
# Specify data location:
urlDict = {"Expenditure":    "jul/jmete/statfin_jmete_pxt_001.px",
           "Deficit":        "jul/jali/statfin_jali_pxt_122g.px"}
# 001 -- General goverment expenditures by function 1990-2016
# 001 -- General government deficit and debt 1975-2017


urlDict2 = {"Debt": "jul/jali/statfinpas_jali_pxt_002_201800.px"}

# 002 -- General government debt, consolidated between sub-sectors 1975-2017


# Perform query:
dgf.getData(urlDict, baseYear = baseYear, active=True)
#%%
# Read in data:
cofogData = {k: pd.read_csv(rawFolder+"/"+str(k)+"_Rawdata.csv",encoding="ISO-8859-1",na_values =".") for k in list(urlDict.keys())}
dgf.getData(urlDict2, baseYear = baseYear, active=False)
cofogData2 = {k: pd.read_csv(rawFolder+"/"+str(k)+"_Rawdata.csv",encoding="ISO-8859-1",na_values =".") for k in list(urlDict2.keys())}
cofogData.update(cofogData2)

#%%
# Clean data:
for i in cofogData:
    cofogData[i].fillna(0, inplace = True)
    if "Data" in cofogData[i].columns:
        cofogData[i].replace({"Current prices": "CP"}, inplace = True)
    
    for col in cofogData[i]:
        if col in ["Sector", "Transaction", "Function"]:
            cofogData[i][col] = cofogData[i][col].apply(lambda x: x.split(" ")[0])  
# Include only current price values:            
cofogData["Expenditure"] = cofogData["Expenditure"][cofogData["Expenditure"]["Data"]=="CP"].reset_index(drop=True)
cofogData["Debt"] = cofogData["Debt"][cofogData["Debt"]["Value"] == "Million Euro"]
#cofogData["Deficit"] = cofogData["Deficit"][cofogData["Deficit"]["Value"] == "Million Euro"]
#cofogData["Deficit"] = [cofogData["Deficit"]["Year"], cofogData["Deficit"]["Sector"], cofogData["Deficit"]["EDP deficit (-) / EDP surplus (+), millions of euro"], cofogData["Deficit"]["EDP debt, millions of euro"]]
#%% [markdown]
# #### Production accounts

#%%
# Specify data location:
urlDict = {
"Production": "kan/vtp/statfinpas_vtp_pxt_007_201700.px",
"Investment": "statfinpas_vtp_pxt_016_201700.px"}
# 007 -- Production and generation of income accounts 1975-2017
# 016 -- Gross fixed capital formation 1975-2017

# Perform query:
dgf.getData(urlDict, baseYear = baseYear, filters = {"Sektori": ["S1", "S1311", "S1313", "S1314"]}, active=False)


#%%
# Read in data: (note the StatFin inconsistency with NaN values)
prodData = {k: pd.read_csv(rawFolder+"/"+str(k)+"_Rawdata.csv",encoding="ISO-8859-1",na_values =[".", ".."])            for k in urlDict.keys()} 


#%%
# Clean data:
for i in prodData:
    prodData[i].fillna(0, inplace = True)
    prodData[i][str(baseYear)] = prodData[i][str(baseYear)].apply(pd.to_numeric, errors = "raise")
    for col in prodData[i]:
        if col in ["Industry", "Sector", "Transaction", "Asset"]:
            prodData[i][col] = prodData[i][col].apply(lambda x: x.split(" ")[0])  
            
        if col == "Information":
            prodData[i].replace({"Current prices": "CP",
                                 "At year 2010 prices": "FP2010"}, inplace = True)  
            
            # Drop redundant info:
            prodData[i].drop(prodData[i][prodData[i].Information.isin(["Changes in volume indices, %",
                                                                          "Ar previous year's prices" # NOTE STATFIN TYPO!!
                                                                      ])].index, inplace=True)
            
        if col == "Industry":
            inds = prodData[i].Industry.unique()
            
            # Fix some StatFin inconsistencies:
            # In some datasets industries are referred to with their aggregate letters, but we want only the 
            # number code format!
            if "D" in inds and not "35" in inds:
                prodData[i].replace({"D": "35"}, inplace = True)           
            if "T" in inds and not "97_98" in inds:
                prodData[i].replace({"T": "97_98"}, inplace = True) 
                
            # And rename the rest following the model naming convention: "011_016" becomes "I_011_016" etc.
            prodData[i][col] = prodData[i][col].apply(lambda x: "{}{}".format("I_", x))
            
            prodData[i].replace({"I_41+432_439": "I_41",
                                 "I_42+431": "I_42_43",
                                 "I_68201_68202":"I_68A",
                                 "I_681+68209+683": "I_68"}, inplace = True)
            


#%%
# Check that each dataset contains all of the industries specified above:
for table in prodData:
    if "Industry" in prodData[table].columns:
        check = set(NIND).issubset(prodData[table].Industry.unique())
        if check:
            print(check, table)
        
        else:
            for ind in prodData:
                if ind not in prodData[table].Industry.unique():
                    print("Missing", ind, "in", table)


#%%
# Before proceeding, take filter a set containing only the industry aggregate "I_0" Industries total to check that
# after manually selecting the nataccIndustries, the entire economy is still covered:
#checkTotals = prodData.copy()
#for table in checkTotals:
#    if "Industry" in checkTotals[table].columns:
#        checkTotals[table] = checkTotals[table][checkTotals[table]["Industry"] == "I_0"]

for table in prodData:
    if "Industry" in prodData[table].columns:
        prodData[table] = prodData[table][prodData[table].Industry.isin(NIND)]
#        prodData[table] = prodData[table].replace(renames)

# Also rename the entries listed in nataccIndustries:
#nataccInd = [renames[i] if i in renames.keys() else i for i in nataccIndustries]


#%%
# Create a mapping from the ~80 national accounts industries to the 30 industries available in regional accounts:
natacc2reg = imf.mapperFunction(NIND, IND)


#%%
# Then, aggregate the industry dimension according to the mapping specified above:
prodDataOLD = {}
for i in prodData:
    prodDataOLD[i] = prodData[i].copy(deep = True)
    
for i in prodData:
    if "Industry" in prodData[i].columns:
        prodData[i]["IND"] = prodData[i]["Industry"].map(natacc2reg)
        groupCols = [x for x in list(prodData[i].columns) if x != "Industry" and x != str(baseYear)]
        prodData[i] = prodData[i].groupby(groupCols, sort = False, as_index = False).sum()#.set_index("IND")


#%%
# Quick check that totals still match after the aggregation:
for sec in prodData["Investment"].Sector.unique():
    check_a = prodDataOLD["Investment"][(prodDataOLD["Investment"]["Sector"] == sec) &
                          (prodDataOLD["Investment"]["Information"] == "CP") &
                          (prodDataOLD["Investment"]["Asset"] == "TOT")][str(baseYear)].sum()
    
    check_b = prodData["Investment"][(prodData["Investment"]["Sector"] == sec) &
                          (prodData["Investment"]["Information"] == "CP") &
                          (prodData["Investment"]["Asset"] == "TOT")][str(baseYear)].sum()
            
    print(abs(check_a - check_b) < 0.1, "for", sec)

#%% [markdown]
# #### Tax data

#%%
# Specify data location:
urlDict = {"Taxes": "jul/vermak/statfin_vermak_pxt_127f.px"}
# 002 -- Taxes and tax-like payments, tax types 1975-2017

# Perform query:
dgf.getData(urlDict, filters = {"Tiedot": ["cp"]}, active=True)


#%%
# Read in data:
taxData = {k: pd.read_csv(rawFolder+"/"+str(k)+"_Rawdata.csv",encoding="ISO-8859-1",na_values =".") for k in urlDict.keys()} 


#%%
# Clean data:
for i in taxData:
    taxData[i].fillna(0, inplace = True)
    if "Data" in taxData[i].columns:
        taxData[i].replace({"Current prices": "CP"}, inplace = True)
    
    for col in taxData[i]:
        if col in ["Sector"]:
            taxData[i][col] = taxData[i][col].apply(lambda x: x.split(" ")[0])


# Include only current price values:            
#taxData["Taxes"] = taxData["Taxes"][taxData["Taxes"]["Data"]=="CP"].reset_index(drop=True)

#%% [markdown]
# ## Step 2: Create government data
# 
# Creates:
# * Extra
# * Forecast file
# * First government data version

#%%
govData = {}


#%%
pubSecs = ["S1311", # Central government
           "S1313", # Local government
           "S1314", # Social security funds
          ]

aggSec = {
"S13":    "S13",    # General government
"S1311":  "S1311",  # Central government
"S1313":  "S1313",  # Local government 
"S13141": "S1314",  # Aggregate: Employment pension schemes -> Social security funds
"S13149": "S1314"   # Aggregate: Other social security funds -> Social security funds
}


#%%
# Aggregate sector accounts according to aggSec specified above:
secBase = sectorData["Sector accounts"].copy()
secBase["aggSector"] = secBase["Sector"].map(aggSec)
secBase = secBase.groupby(["aggSector", "Transaction"], sort = False).sum().reset_index()

govBase = sectorData["Govt accounts"].copy()
govBase["aggSector"] = govBase["Sector"].map(aggSec)
govBase = govBase.groupby(["aggSector", "Transaction"], sort = False).sum().reset_index()

# Also, filter out COFOG expenture by function data for the next step:
cofog = cofogData["Expenditure"].copy()


#%%
# Read current priced employers' social contributions from production accounts data:
govData["D1"] =  prodData["Production"][(prodData["Production"]["Transaction"] == "D1K") &                       (prodData["Production"]["Sector"] == "S1") &                       (prodData["Production"]["Information"] == "CP")].set_index("IND")[str(baseYear)]


govData["D12"] = prodData["Production"][(prodData["Production"]["Transaction"] == "D12K") &                       (prodData["Production"]["Sector"] == "S1") &                       (prodData["Production"]["Information"] == "CP")].set_index("IND")[str(baseYear)]

# Read in D61R Social contributions from sector accounts:
govData["D61"] = secBase[(secBase["aggSector"].isin(pubSecs)) &                         (secBase["Transaction"] == "D61R")].set_index("aggSector", drop = True)[str(baseYear)]

govData["D12SHR"] = govData["D12"] / govData["D12"].sum()

d61 = pd.DataFrame(govData["D61"])
d12shr = pd.DataFrame(govData["D12SHR"])


#%%
# Payroll:
govData["PAYR"] = d12shr.dot(d61.T)
# Payroll share:
govData["PAYRSHR"] = govData["PAYR"].divide(govData["D1"], axis = 0) 
# Payroll 2:
govData["PAYR2"] = govData["PAYRSHR"].multiply(V1LAB_O, axis = 0)
# Payroll sum:
govData["PAYRSUM"] = govData["PAYR2"].sum(axis=1)


#%%
# !Luetaan palkansaajakorvaukset ja pääomakorvaukset uudelleen!
# !Tämä, jotta julkinen sektori menee tasapainoon muokatun
# tietokannan kanssa!
govData["D11"] = V1LAB_O - govData["PAYRSUM"] 
# Power of payroll tax
govData["POW_PAYROLL"] = (V1LAB_O / govData["D11"]).fillna(0)

# Power of payroll tax by sectors
govData["POW_PAYROLL2"] = pd.DataFrame(0.0, index = pubSecs, columns = IND)

govData["POW_PAYROLL2"].loc["S1311"] = ((govData["D11"] + govData["PAYR2"]["S1311"]) / govData["D11"]).fillna(0)
govData["POW_PAYROLL2"].loc["S1313"] = ((govData["D11"] + govData["PAYR2"]["S1313"]) / govData["D11"]).fillna(0)
govData["POW_PAYROLL2"].loc["S1314"] = ((govData["D11"] + govData["PAYR2"]["S1314"]) / govData["D11"]).fillna(0)

govData["BETA_PAYROLL"] = govData["POW_PAYROLL2"] -1 

# For checking:
govData["COL_PAYROLL"] = govData["PAYRSUM"].copy()
govData["PAYRTOT"] = govData["COL_PAYROLL"].sum()


#%%
# Test match:
t1 = govData["D11"] * (govData["POW_PAYROLL"]-1)
t2 = govData["D11"] * (govData["POW_PAYROLL2"]-1)
t3 = t1 - t2.sum()
# Check that the difference is negligible:
all(abs(t3)<000.1)

#%% [markdown]
# ### Public sector expenditure:

#%%
expTypes = ["PROPINC",     # Property expenditure excluding interest payments (Sector acc: D4K - D41K)
            "INCTAX",      # Income taxes (Sector acc: D51K)
            "OTHTAX",      # Other current taxes (Sector acc: D59K)
            "AGEBEN",      # Old age (COFOG: Transaction = D62K, Function = G1002)
            "UNEMPBEN",    # Unemployment (COFOG: Transaction = D62K, Function = G1005)
            "OTHBEN",      # Other benefits (Sector acc: D62K - AGEBEN - OTHBEN)
            "GRANTS",      # GNI payment to EU + miscellanious current transfers (D761K+D759KS11+D759KS14+D759KS15)
            "CURTFS",      # Current transfers (Sector acc: D71K + D72K + D74K)
            "CAPTFS",      # Capital transfers (Sector acc: D9K + P51CK Consumption of fixed capital)
            "OTHCAPGOV",   # Other government expenditure (PROPINC + INCTAX + OTHTAX + CURTFS + CAPTFS)
            "TAX_AB_RATE", # Tax rate for all benefits
            "TAX_OB_RATE", # Tax rate for  other benefits
            "TAX_UB_RATE", # Tax rate for  unemployment benefits
           ]


#%%
# Initialize an empty dataframe:
DTE = pd.DataFrame(0.0, index = expTypes, columns = pubSecs)


#%%
for s in pubSecs:
    value = str(baseYear)
    DTE.loc["PROPINC"][s] =    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D4K")][value])-    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D41K")][value])
    
    DTE.loc["INCTAX"][s] =    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D51K")][value])
    
    DTE.loc["OTHTAX"][s] =    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D59K")][value])
    
    DTE.loc["AGEBEN"][s] =    float(cofog[(cofog["Sector"] == s) & (cofog["Function"] == "G1002") & (cofog["Transaction"] == "D62K")][value])
    
    DTE.loc["UNEMPBEN"][s] =    float(cofog[(cofog["Sector"] == s) & (cofog["Function"] == "G1005") & (cofog["Transaction"] == "D62K")][value])
    
    DTE.loc["OTHBEN"][s] =    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D62K")][value])-    DTE.loc["AGEBEN"][s] - DTE.loc["UNEMPBEN"][s]

    DTE.loc["GRANTS"][s] =    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D761K")][value]) +    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D759KS11")][value]) +    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D759KS14")][value]) +    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D759KS15")][value])
    
    DTE.loc["CURTFS"][s] =    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D71K")][value]) +    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D72K")][value]) +    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D74K")][value])
    
    DTE.loc["CAPTFS"][s] =    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D9K")][value]) +    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "P51CK")][value])
    
    DTE.loc["OTHCAPGOV"][s] =    DTE.loc["PROPINC"][s] + DTE.loc["INCTAX"][s] + DTE.loc["OTHTAX"][s] + DTE.loc["CURTFS"][s] + DTE.loc["CAPTFS"][s]


#%%
# Tax rates on benefits. PÄIVITÄ TÄHÄN UUDET LUVUT! NÄMÄ OTETTU SUORAAN VANHASTA TIETOKANNASTA!!
DTE.loc["TAX_AB_RATE"] = {"S1311": 0.080, "S1313": 0.164, "S1314": 0}
DTE.loc["TAX_OB_RATE"] = {"S1311": 0.053, "S1313": 0.168, "S1314": 0}
DTE.loc["TAX_UB_RATE"] = {"S1311": 0.053, "S1313": 0.168, "S1314": 0}


#%%
# Tax collected from age benefit income
govData["TAX_AB"] = DTE.loc["TAX_AB_RATE"] * DTE.loc["AGEBEN"].sum()
# Tax collected from other benefit income
govData["TAX_OB"] = DTE.loc["TAX_OB_RATE"] * DTE.loc["OTHBEN"].sum()
# Tax collected from unemployment benefit income
govData["TAX_UB"] = DTE.loc["TAX_UB_RATE"] * DTE.loc["UNEMPBEN"].sum()

#%% [markdown]
# ### Public debt and interets rate

#%%
# Public sector debt:
govData["PSDATT"] = cofogData["Debt"].set_index("Sector").reindex(pubSecs)[str(baseYear)]
# Interest payments (Sector accounts: D41K Interest, payable (FISIM-adjusted))
govData["NETINT_G"] = secBase[secBase["Transaction"] == "D41K"].set_index("aggSector").reindex(pubSecs)[str(baseYear)]
# Interest income (Sector accounts: D41R Interest, receivable (FISIM-adjusted))
govData["INTASS"] = secBase[secBase["Transaction"] == "D41R"].set_index("aggSector").reindex(pubSecs)[str(baseYear)]


#%%
# Real rate of interest on public sector debt
govData["RINT_PSD"] = govData["NETINT_G"] / ((govData["PSDATT"] + govData["PSDATT"] + govData["NETINT_G"])/2)
govData["RINT_PSD_S"] = govData["NETINT_G"].sum() / ((govData["PSDATT"] + govData["PSDATT"] + govData["NETINT_G"]).sum()/2)

#%% [markdown]
# ### Public sector income

#%%
incTypes = ["PROFIT",    # Sector accounts: B13GT Operating surplus
            "PROPINC",   # Property income excluding interest payments (Sector accounts: D4R - D41R)
            "SRCTAX",    # Taxes and tax-like payments: "-1000 Duty on interests"
            "INCTAX",    # Taxes and tax-like payments: "-1000 Income tax of households"
            "CORPTAX",   # Taxes and tax-like payments: "-1000 Income tax of corporations"
            "OTHTAX",    # Other income tax. Sector accounts D51R Income taxes - SRCTAX - INCTAX - CORPTAX  
            "MAINFEE",   # Taxes and tax-like payments: "-4000 Tax on real-estate" (kiinteistövero)
            "OTHFEE",    # Sector accounts: D59R Other current taxes, excl. tax on capital - MAINFEE
            "CURTFS",    # Sector accounts: D7R Other current transfers, receivable - D73R transfers within government
            "CAPTFS",    # Sector accounts: D9R Capital transfers + P51CR Consumption of fixed capital
            "PAYROLL",   # Sector accounts: D61R Social contributions
            "NETPTAX",   # Sector accounts: D2R Taxes on production - D3K Subsidies
            "OTHGOVREV", # CURTFS + CAPTFS + PROFIT + PROPINC
            # Varallisuusverot HHPROPFEE ja CORPPROPFEE lakkautettu 2006
]


#%%
# Initialize an empty dataframe:
DTI = pd.DataFrame(0.0, index = incTypes, columns = pubSecs)

taxBase = taxData["Taxes"].copy()
taxBase = taxBase[taxBase["Sector"].isin(pubSecs)]

#Rename columns
#Example: From '2018 Current prices, millions of euro' TO '2018'
for i in range(2,len(taxBase.keys()),1):
    n=taxBase.keys()[i][0:4]
    taxBase.rename(columns={taxBase.keys()[i]:n}, inplace=True)

#%%
for s in pubSecs:
    value = str(baseYear)
    DTI.loc["PROFIT"][s] =    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "B13GT")][value])
    
    DTI.loc["PROPINC"][s] =    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D4R")][value]) -    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D41R")][value])
    
    #DTI.loc["SRCTAX"][s] =    float(taxBase[(taxBase["Sector"] == s) & (taxBase["Tax category"] == "-1000 Duty on interests")][value])
    DTI.loc["SRCTAX"][s] =    float(taxBase[(taxBase["Sector"] == s) & (taxBase["Tax category"] == "110001 Duty on interests")][value])
    #DTI.loc["INCTAX"][s] =    float(taxBase[(taxBase["Sector"] == s) & (taxBase["Tax category"] == "-1000 Income tax of households")][value])
    DTI.loc["INCTAX"][s] =    float(taxBase[(taxBase["Sector"] == s) & (taxBase["Tax category"] == "110002 Income tax of households")][value])
    
    #DTI.loc["CORPTAX"][s] =    float(taxBase[(taxBase["Sector"] == s) & (taxBase["Tax category"] == "-1000 Income tax of corporations")][value])
    DTI.loc["CORPTAX"][s] =    float(taxBase[(taxBase["Sector"] == s) & (taxBase["Tax category"] == "120001 Income tax of corporations")][value])

    DTI.loc["OTHTAX"][s] =    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D51R")][value]) -    DTI.loc["SRCTAX"][s] - DTI.loc["INCTAX"][s] - DTI.loc["CORPTAX"][s]
    
    #DTI.loc["MAINFEE"][s] =    float(taxBase[(taxBase["Sector"] == s) & (taxBase["Tax category"] == "-4000 Tax on real-estate")][value])
    DTI.loc["MAINFEE"][s] =    float(taxBase[(taxBase["Sector"] == s) & (taxBase["Tax category"] == "410001 Tax on real-estate")][value])

    DTI.loc["OTHFEE"][s] =    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D59R")][value]) -    DTI.loc["MAINFEE"][s]
    
    DTI.loc["CURTFS"][s] =    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D7R")][value]) -    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D73R")][value])
    
    DTI.loc["CAPTFS"][s] =    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D9R")][value]) +    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "P51CR")][value])
    
    DTI.loc["PAYROLL"][s] =    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D61R")][value])
    
    DTI.loc["NETPTAX"][s] =    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D2R")][value]) -    float(secBase[(secBase["aggSector"] == s) & (secBase["Transaction"] == "D3K")][value])
    
    DTI.loc["OTHGOVREV"][s] =    DTI.loc["CURTFS"][s] + DTI.loc["CAPTFS"][s] + DTI.loc["PROFIT"][s] + DTI.loc["PROPINC"][s]

#%% [markdown]
# #### Transfer tax on inventories to other government income:

#%%
DTI.loc["OTHGOVREV"]["S1311"] += V6TAX_CS

#%% [markdown]
# #### Calculate tax rate on salaries and capital income

#%%
# Calculate tax on labour by industries.
# Income tax is split between labour income and capital income shares (0.67 and 0.33 respectively)
govData["TAX_LAB"] =DTI.loc["INCTAX"] * 0.67 + DTI.loc["OTHTAX"] + DTI.loc["OTHFEE"] - govData["TAX_AB"] - govData["TAX_OB"] - govData["TAX_UB"]
govData["TAX_L_RATE"] = govData["TAX_LAB"] / (V1LAB_O.sum() - govData["COL_PAYROLL"].sum())

#%% [markdown]
# #### Rate of tax on capital by industries

#%%
govData["TAX_CL"] = DTI.loc["INCTAX"] * 0.33 + DTI.loc["SRCTAX"] + DTI.loc["CORPTAX"]
govData["TAX_K_RATE"] = govData["TAX_CL"] / (V1CAP.sum() + V1LND.sum())
govData["TAX_CAP"] = govData["TAX_K_RATE"] * V1CAP.sum()
govData["TAX_LND"] = govData["TAX_K_RATE"] * V1LND.sum()

#%% [markdown]
# ####  TARKISTUS 1: VASTAAKO JULKISYHTEISÖJEN TULOT ALKUPERÄISTÄ, EI KORKOJA !

#%%
govData["INCTAX"] = govData["TAX_LAB"] + govData["TAX_CAP"] + govData["TAX_LND"] +                    govData["TAX_AB"] + govData["TAX_OB"] + govData["TAX_UB"]
govData["INCTAX_S"] = govData["INCTAX"].sum()


#%%
govData["NET_TAXTOTG"] = DTI.loc["NETPTAX"].sum() + govData["TAX_CL"].sum() + govData["TAX_LAB"].sum() +                         govData["TAX_AB"].sum() + govData["TAX_OB"].sum() + govData["TAX_UB"].sum() + DTI.loc["PAYROLL"].sum()


#%%
govData["NET_TAXTOT2"] = V0TAX_CSI + govData["INCTAX_S"] + govData["PAYRTOT"]


#%%
# The difference between input output data and sector accounts:
# (The difference will be allocated to other government revenue)
govData["DIFFTAX"] = govData["NET_TAXTOTG"] - govData["NET_TAXTOT2"]


#%%
govData["DIRECTINC"] = govData["INCTAX_S"] + DTI.loc["OTHGOVREV"].sum() + govData["PAYRTOT"] - V6TAX_CS


#%%
# TÄMÄ HEITTÄÄ PALJON!!!!
ALLOLD = DTI.sum().sum()
ALLNEW = govData["DIRECTINC"]
ALLDIF = ALLOLD - ALLNEW

#%% [markdown]
# #### Julkisten menojen kohdentuminen eri sektoreille

#%%
# Sum values of government expenditure:
expenditures = [
"D1K",   # Compensation of employees
"D29K",  # Other taxes on production
"D3K",   # Subsidies
"D4K",   # Property expenditure
"D5K",   # Current taxes on income and wealth, etc., payable
"D61K",  # Social contributions, payable
"D62K",  # Social benefits other than social transfers in kind, payable
"D631K", # Social transfers in kind – non-market production
"D7K",   # Other current transfers, payable
"D8K",   # Adjustment for the change in pension entitlements
"D9K",   # Capital transfers, payable
"P2K",   # Intermediate consumption
"P3K",   # Final consumption expenditure
"P51K",  # Gross fixed capital formation
"P52K",  # Changes in inventories
"P53K",  # Net acquisitions of valuables
]


#%%
PEX = secBase[(secBase["aggSector"].isin(pubSecs)) & (secBase["Transaction"].isin(expenditures))].reset_index(drop = True)


#%%
ALLEXPDATA =govData["NETINT_G"] +PEX[PEX["Transaction"] == "P2K"].set_index("aggSector")[str(baseYear)] +PEX[PEX["Transaction"] == "D1K"].set_index("aggSector")[str(baseYear)] +PEX[PEX["Transaction"] == "D29K"].set_index("aggSector")[str(baseYear)]+DTE.loc["PROPINC"] +DTE.loc["INCTAX"]  +DTE.loc["OTHTAX"]  +PEX[PEX["Transaction"] == "D61K"].set_index("aggSector")[str(baseYear)] +PEX[PEX["Transaction"] == "D62K"].set_index("aggSector")[str(baseYear)] +PEX[PEX["Transaction"] == "D631K"].set_index("aggSector")[str(baseYear)]+DTE.loc["CURTFS"] +DTE.loc["GRANTS"] +PEX[PEX["Transaction"] == "D8K"].set_index("aggSector")[str(baseYear)] +DTE.loc["CAPTFS"] +PEX[PEX["Transaction"] == "P51K"].set_index("aggSector")[str(baseYear)] +PEX[PEX["Transaction"] == "P52K"].set_index("aggSector")[str(baseYear)] +PEX[PEX["Transaction"] == "P53K"].set_index("aggSector")[str(baseYear)]


#%%
V5TOT2 = V5BAS.sum().sum() + V5MAR_CSM + V5TAX_CS


#%%
P3 = PEX[PEX["Transaction"] == "P3K"].set_index("aggSector")[str(baseYear)]
P3SUM = P3.sum()
P3SHR = P3 / P3SUM
V5TOT = P3SHR * V5TOT2

#%% [markdown]
# #### Public sector investment share 

#%%
invests = prodData["Investment"][(prodData["Investment"]["Information"] == "CP") &                                 (prodData["Investment"]["Asset"] == "TOT") 
                                ].reset_index(drop = True)


#%%
# Government investment:
GOVI = invests[invests["Sector"].isin(pubSecs)].reset_index(drop=True)
# All investments:
ALLI = invests[invests["Sector"] == "S1"].set_index("IND")[str(baseYear)]


#%%
# Check for negative values in investments:
cfs.check4negs(pd.DataFrame(GOVI[str(baseYear)]))


#%%
# Set negatives to zero:
flag = True
for i in GOVI.index:
    value = GOVI.iloc[i][str(baseYear)]
    if value < 0:
        flag = False
        GOVI.loc[i, str(baseYear)] = 0
        loca = GOVI.loc[i]["IND"]
        sect = GOVI.loc[i]["Sector"]
        print(loca, sect, value, "set to zero!")
        
        # ALLI is adjusted in order to avoid situation where government share of investments is > 1
        ALLI.loc[loca] += abs(value)
        
if flag:
    print("OK! No negative values found!")


#%%
INVSHR = pd.DataFrame(0.0, index = IND, columns = pubSecs)
for s in pubSecs:
    for i in IND[:-1]: # Disregard I_97. It is zero and causes division errors,
        govInvest = float(GOVI[(GOVI["Sector"] == s) & (GOVI["IND"] == i)][str(baseYear)])
        allInvest = float(ALLI.loc[i])
        
        govShr = govInvest / allInvest
        
        INVSHR.loc[i][s] = govShr


#%%
V2TOT = V2PUR_CS
INVS = INVSHR.multiply(V2TOT, axis = "index")

#%% [markdown]
# #### Transfers between sectors
#%% [markdown]
# # Calculate transfers between sectors by subtracting the consolidated value from payable data:

#%%
transferTypes = [
"D4", # D4K Property expenditure
"D7", # D7K Other current transfers, payable
"D9", # D9K Capital transfers, payable
]


#%%
for t in transferTypes:
    govData[t] = pd.Series(0.0, index = pubSecs)
    for s in pubSecs:
        paid = float(govBase[(govBase["aggSector"] == s) & (govBase["Transaction"] == t+"K")][str(baseYear)])
        cons = float(govBase[(govBase["aggSector"] == s) & (govBase["Transaction"] == t+"SK")][str(baseYear)])
        
        transfer = paid - cons
        govData[t].loc[s] = transfer


#%%
# All transfers between public sectors
govData["PTRANS"] = govData["D4"] + govData["D7"] + govData["D9"]


#%%
# Check that the sum matches raw data totals:
total = govBase[(govBase["Transaction"] == "TOTEXP") & govBase["aggSector"].isin(pubSecs)][str(baseYear)].sum()
consolidated = govBase[(govBase["Transaction"] == "TOTEXPS") & (govBase["aggSector"] == "S13")][str(baseYear)].sum()

abs(total - consolidated -govData["PTRANS"].sum()) < 0.001

#%% [markdown]
# #### Balancing other government expenditure

#%%
V2TOT_G_I = INVS.sum()

#%% [markdown]
# #### Checking government deficit

#%%
# All expenditures
expflows = V5TOT + V2TOT_G_I + DTE.loc["OTHCAPGOV"] + DTE.loc["UNEMPBEN"] + DTE.loc["AGEBEN"] +           DTE.loc["OTHBEN"] + DTE.loc["GRANTS"] + govData["NETINT_G"]


#%%
# All income + difference
revflows = govData["NET_TAXTOT2"] + DTI.loc["OTHGOVREV"].sum() + govData["DIFFTAX"]


#%%
# Julkisen sektorin nettoluotonanto
surplus = revflows - expflows.sum()
# Perusjäämä
psurplus = revflows - expflows.sum() - govData["INTASS"].sum() + govData["NETINT_G"].sum()

#%% [markdown]
# #### Checking public sector debt 
# 
# Luetaan sulautettu valtio ja korko
# 
# Lasketaan julkisen sektorin korkomenot/julkisen sektorin velka
# 
# Oletetaan, että velka muodostuu ainoastaan valtion ja paikallishallinnon
# alijäämistä. Vähennetään siis kokonaisalijäämästä sosiaaliturvarahastojen
# alijäämä (sektoritilinpidosta)

#%%
# Social security funds deficit/surplus

SSSURPLUS = float(cofogData["Deficit"][(cofogData["Deficit"]["Sector"] == "S1314")]["EDP deficit (-) / EDP surplus (+), millions of euro"])

#%%
# Velka tilastovuoden lopussa
PSDATTPLUS2 = govData["PSDATT"].sum() - psurplus + SSSURPLUS

#%% [markdown]
# #### Splitting data between government sectors. THIS MIGHT NEED REVISION!

#%%
# Using COFOG expenditures to estimate government consumption by sector and by commodity:
com2gov = {
"C_01":    "G0", # Agriculture and hunting -> All functions
"C_02_03": "G0", # Forestry, Fishing -> 
"C_05_09": "G0", # Mining and quarrying -> 
'C_10_12': "G0", # Food industry, etc. -> 
'C_13_15': "G0", # Textile, clothing -> 
'C_16':    "G0", # Woodworking -> 
'C_17_18': "G0", # Paper industry ->  All functions
'C_19_22': "G07", # Chemical industry -> Health
'C_23':    "G0", # Non-metallic mineral products ->  All functions
'C_24_25': "G0", # Basic metals -> 
'C_26_27': "G0", # Electrical and electronic products -> 
'C_28':    "G0", # Machinery and equipment -> 
'C_29_30': "G0", # Transport equipment -> 
'C_31_33': "G0", # Furniture / Other manucturing -> 
'C_35_39': "G0", # Water supply and waste management -> 
'C_41_43': "G0", # Construction -> 
'C_45_47': "G0", # Trade and repair of motor vehicles -> 
'C_49_53': "G0", # Transportation and storage -> 
'C_55_56': "G0", # Accommodation and food service -> 
'C_58_63': "G0", # Publishing activities -> 
'C_64_66': "G0", # Financial and insurance activities -> 
'C_68':    "G0", # Other real estate activities -> 
'C_68A':   "G0", # Letting and operation of dwellings -> 
'C_69_75': "G0", # Professional, scientific and technical activities -> 
'C_77_82': "G01",   # Administrative and support service activities -> General public services
'C_84':    "G0",   # Public administration and social security -> All functions  
'C_85':    "G09",   # Education -> Education
'C_86_88': "G07",   # Human health and social work activities -> Health ! Should include also social protecton, but share is pretty same
'C_90_96': "G08",   # Arts, entertainment and recreation -> Recreation, culture and religion
'C_97_98': "G0",    # Household service activities -> All functions
}


#%%
sectorShares = pd.DataFrame(0.0, index = COM, columns = pubSecs)


#%%
for c in COM:
    for s in pubSecs:
        mapping = com2gov[c]
        total = float(cofog[(cofog["Sector"] == "S13") &                      (cofog["Transaction"] == "P3K") &                      (cofog["Function"] == mapping)][str(baseYear)])
        sectorLevel = float(cofog[(cofog["Sector"] == s) &                      (cofog["Transaction"] == "P3K") &                      (cofog["Function"] == mapping)][str(baseYear)])
        

        sectorShare = sectorLevel / total
        
        sectorShares.loc[c][s] = sectorShare
    if abs(sectorShares.loc[c].sum()-1) > 0.0001:
        raise ValueError("Share totals do not match for", c)


#%%
V5BASPdom = sectorShares.multiply(V5BAS["DOM"], axis = "index")
V5BASPimp = sectorShares.multiply(V5BAS["IMP"], axis = "index")

V5TAXPdom = sectorShares.multiply(V5TAX["DOM"], axis = "index")
V5TAXPimp = sectorShares.multiply(V5TAX["IMP"], axis = "index")


#%%
govMargins = {}
for m in MAR:
    index = MAR.index(m)
    govMargins[m] = pd.DataFrame(V5MAR[:,0:,index].copy(), index = COM, columns = SRC)
    for s in SRC:
        govMargins["FRAME"+"_"+s+"_"+m] = pd.DataFrame(0.0, index = COM, columns = pubSecs)
        govMargins[m+s] = govMargins[m][s]
        for p in pubSecs:
            value = govMargins[m+s] * sectorShares[p]
            govMargins["FRAME_"+s+"_"+m][p] = value


#%%
#note dstack = along the 3rd dimension for margins!
V5MARP = np.stack([
np.dstack([govMargins[key].values for key in govMargins.keys() if "FRAME" in key and "DOM" in key]),\
np.dstack([govMargins[key].values for key in govMargins.keys() if "FRAME" in key and "IMP" in key])], axis=1)

#%% [markdown]
# # Write govdagg.har ja extradagg.har

#%%
govDims = {
"IND": IND,
"COM": COM,
"PSEC": pubSecs,
"SRC": SRC,
"MAR": MAR
}


#%%
V5BASP = np.stack((V5BASPdom.values, V5BASPimp.values), axis=1)
V5TAXP = np.stack((V5TAXPdom.values, V5TAXPimp.values), axis=1)


#%%
govDagg = {
#coefficient name: (dataname, header name, long name, [list of dimensions])
"OTHCAPGOV": (DTE.loc["OTHCAPGOV"], "OGI2", "Other government expenditure", ["PSEC"]),    
"UNEMPBEN":  (DTE.loc["UNEMPBEN"], "UBEN", "Unemployment benefits", ["PSEC"]),    
"AGEBEN":    (DTE.loc["AGEBEN"], "AGEB", "Age benefits", ["PSEC"]),    
"OTHBEN":    (DTE.loc["OTHBEN"], "OTHB", "Other benefits", ["PSEC"]),  
"GRANT":     (DTE.loc["GRANTS"], "GRNT", "Other transfers abroad", ["PSEC"]),  
"PSDATT":    (govData["PSDATT"], "PSDT", "Public sector debt, start of year", ["PSEC"]),  
"NETINT_G":  (govData["NETINT_G"], "NINT", "Interest payments", ["PSEC"]),
"INTASS":    (govData["INTASS"], "INTA", "Interest income", ["PSEC"]),
    
"RINT_PSD":   (govData["RINT_PSD"], "GRIT", "Real rate of interest on public sector debt", ["PSEC"]),
"RINT_PSD_S": (govData["RINT_PSD_S"], "GRIS", "Real rate of interest on public sector debt, aggregate", []),
    
"OTHGOVREV": (DTI.loc["OTHGOVREV"], "OTGR", "Other government income, mio", ["PSEC"]),
    
"TAX_AB_RATE": (DTE.loc["TAX_AB_RATE"], "TLAB", "Tax rate for all benefits", ["PSEC"]),
"TAX_OB_RATE": (DTE.loc["TAX_OB_RATE"], "TLOB", "Tax rate for other benefits", ["PSEC"]),
"TAX_UB_RATE": (DTE.loc["TAX_UB_RATE"], "TLUB", "Tax rate for unemployment benefits", ["PSEC"]),
    
"CORPTAX": (DTI.loc["CORPTAX"], "YVER", "Corporate tax, yhteisovero", ["PSEC"]),
"DIFFTAX": (govData["DIFFTAX"], "DIFT", "Difference in income - expenditure", []),  
    
"V5TOT":  (V5TOT, "5SEC", "Total value of government demands by sector", ["PSEC"]),   
"INVSHR": (INVSHR, "GVSH", "Government share of investments", ["IND","PSEC"]),   
"INVS":   (INVS, "INVS", "Government investments", ["IND","PSEC"]),
"V2TOT":  (V2TOT, "2TOT", "Total capital created for industry i", ["IND"]),  
    
"D4": (govData["D4"], "D4", "Other capital transfers between public sectors", ["PSEC"]),   
"D7": (govData["D7"], "D7", "Other transfers between public sectors", ["PSEC"]),  
"D9": (govData["D9"], "D9", "Investment grants and capital transfers between public sectors", ["PSEC"]), 
"PTRANS":    (govData["PTRANS"], "PTRS", "All transfers between public sectors", ["PSEC"]),    
"SSSURPLUS": (SSSURPLUS, "5SSP", "Social security funds surplus", []),     
    
"V5BASP": (V5BASP, "5BSS", "Government basic", ["COM", "SRC", "PSEC"]),  
"V5TAXP": (V5TAXP, "5TAS", "Government tax", ["COM", "SRC", "PSEC"]),  
"V5MARP": (V5MARP, "5MAS", "Government margins", ["COM", "SRC", "PSEC", "MAR"]),
"V5TOTP": (V5TOT, "5TOT", "Total value of government demands", ["PSEC"]),   
}


#%%
output = {**govDims, **govDagg}
hwf.data2har(output, govDims).writeToDisk(harFolder+"/govdata.har")


#%%
extraDagg = {
#coefficient name: (dataname, header name, long name, [list of dimensions])
"POW_PAYROLL":    (govData["POW_PAYROLL"], "POPR", "Power of payroll tax", ["IND"]),    
"POW_PAYROLL2":    (govData["POW_PAYROLL2"], "POP2", "Power of payroll tax by sector", ["PSEC", "IND"]),    
"V1LAB_O":    (V1LAB_O, "1LAB", "Total payments to labour", ["IND"]),  
"PAYR":    (govData["PAYR2"].T, "PAYR", "Total social benefits to labour", ["PSEC", "IND"]),  
"TAX_L_RATE":    (govData["TAX_L_RATE"], "TLRT", "Rate of tax on labour by industries", ["PSEC"]),  
"TAX_K_RATE":    (govData["TAX_K_RATE"], "TAXK", "Rate of tax on capital by industries", ["PSEC"]),  
}


#%%
output = extraDagg
hwf.data2har(output, govDims).writeToDisk(harFolder+"/govextra.har")

#%% [markdown]
# ### POWEDIT
# 
# tuottaa uuden tiedoston GOVSECSPLIT.har, joka sisältää tietoa edeltävässä askeleessa luoduista tiedostoista GOVDAGG.har ja EXTRADAGG.har sekä muutaman uuden headerin. Uudet headerit sisältävät power-muotoisia parametrejä palkkaveroista sekä julkisista investoinneista (tasot ja osuudet). 

#%%
powedit = {}
powedit["PAYR2"] = govData["PAYR2"].copy()
powedit["PAYRSUM"] =powedit["PAYR2"].sum(axis=1)


#%%
powedit["D11K"] = V1LAB_O - powedit["PAYRSUM"]
# Power of payroll tax by industries:
powedit["POW_PAYROLL"] = (V1LAB_O / powedit["D11K"]).fillna(1)


#%%
# Power of payroll tax by industries and sectors:
powedit["POW_PAYROLL2"] = pd.DataFrame(0.0, index = IND, columns = pubSecs)
for p in pubSecs:
    powedit["POW_PAYROLL2"][p] = ((powedit["PAYR2"][p] + powedit["D11K"]) / powedit["D11K"]).fillna(1)


#%%
test11_1 = powedit["D11K"] * (powedit["POW_PAYROLL"]-1)
test11_2 = (powedit["POW_PAYROLL2"]-1).multiply(powedit["D11K"], axis = "index")
test11_C = test11_1 - test11_2.sum(axis=1)

all(abs(test11_C) < 0.1)


#%%
powOut = {
#coefficient name: (dataname, header name, long name, [list of dimensions])
"V1LAB_O":      (V1LAB_O, "1LAB", "Total payments to labour", ["IND"]),  
"PAYR2":        (powedit["PAYR2"], "PAYR", "Total social security payments to labour", ["IND", "PSEC"]),  
"POW_PAYROLL2": (powedit["POW_PAYROLL2"], "POPS", "Power of payroll tax by sector", ["IND", "PSEC"]),  
"TAX_L_RATE":   (govData["TAX_L_RATE"], "TLRS", "Rate of tax on labour by industries", ["PSEC"]),  
"TAX_K_RATE":   (govData["TAX_K_RATE"], "TXKS", "Rate of tax on capital by industries", ["PSEC"]),  
"POW_PAYROLL":  (powedit["POW_PAYROLL"], "POPR", "Power of payroll tax", ["IND"]),  
#"POW_PAYROLL2":      (powedit["POW_PAYROLL2"], "PPRS", "Power of payroll tax by sector", ["IND", "PSEC"]),  
    }


#%%
output = {**powOut, **govDagg}
hwf.data2har(output, govDims).writeToDisk(harFolder+"/govsecsplit.har")

#%% [markdown]
# # END OF PROGRAM
# 

