#%% [markdown]
# # Capital data for model dynamics
# 
# This notebook creates trend files for capital dynamics, and also the EXTRA files required by the model.
# 
# See the equations list at https://www.copsmodels.com/ftp/monbook1/m1-ch4t.pdf

#%%
# Import all necessary modules:

# Basic modules
import requests
import pandas as pd
import numpy  as np
import json
import ast
import csv
import os
import re

# HARPY module by Centre of Policy Studies for writing data into Header Array (HAR) format.
# Available at https://github.com/GEMPACKsoftware/HARPY
from harpy.har_file import HarFileObj
from harpy.header_array import HeaderArrayObj as HAO

import dataGetterFunction as dgf
import harWriterFunction  as hwf
import mapperFunction as imf


#%%
# Choose base year for data:
baseYear = 2015
# Raw data folder:
rawFolder = "rawdata"
# Folder for output HAR-files:
harFolder = "hardata"


#%%
# Read data from previous steps:
baseData = HarFileObj.loadFromDisk(harFolder+"/basedata.har")


#%%
# Read sets from the national.har basedata:
IND = baseData.getHeaderArrayObj("IND")["array"].tolist()
REG = baseData.getHeaderArrayObj("REG")["array"].tolist()
COM = baseData.getHeaderArrayObj("COM")["array"].tolist()
SRC = baseData.getHeaderArrayObj("SRC")["array"].tolist()
OCC = baseData.getHeaderArrayObj("OCC")["array"].tolist()
# HarFileObj leaves some trailing whitespaces to some entries (this may have changed in more recent versions). 
# Remove them with:
IND = [i.strip(' ') for i in IND]
REG = [r.strip(' ') for r in REG]
COM = [c.strip(' ') for c in COM]
SRC = [s.strip(' ') for s in SRC]
OCC = [o.strip(' ') for o in OCC]

#%% [markdown]
# ### Query capital data from national accounts:
# 
# Available time series start from 1975, which makes the default data requests bigger than the allowed 110K entries. The queries must therefore be broken up to smaller segments.

#%%
urlDict = {
"Capital formation":           "kan/vtp/statfinpas_vtp_pxt_016_201700.px",
"Consumption and retirement":  "kan/vtp/statfinpas_vtp_pxt_017_201700.px",
}
# 016 -- Gross fixed capital formation 1975-2017
# 017 -- Gross capital, Net capital, consumption and retirements of fixed capital 1975-2017

dgf.getData(urlDict, filters={"Sektori": ["S1"], "Vara": ["TOT"]}, active=False)


#%%
urlDict2 = {"Employment": "kan/vtp/statfinpas_vtp_pxt_008_201700.px"}
# 008 -- Employment and hours worked 1975-2017

dgf.getData(urlDict2, filters={"Sektori": ["S1"]})


#%%
urlDict3 = {"Production accounts": "kan/vtp/statfinpas_vtp_pxt_007_201700.px"}
# 007 -- Production and generation of income accounts 1975-2017

dgf.getData(urlDict3, filters = {"Sektori": ["S1"], "Taloustoimi": ["B2NT", "B3NT", "P51CK"]})

# The filters used above are:
# S1    = Total economy
# TOT   = All assets
# B2NT  = Operating surplus 
# B3NT  = Mixed income
# P51CK = Consumption of fixed capital


#%%
# Read in data:
nataccData = {k: pd.read_csv(rawFolder+"/"+str(k)+"_Rawdata.csv",encoding="ISO-8859-1",na_values =".")              for k in list(urlDict.keys()) + list(urlDict2.keys()) + list(urlDict3.keys())}

#%% [markdown]
# ### Clean the dta

#%%
# Collect here the entire available time period (up to the baseYear specified earlier):
fullPeriod = []

for i in nataccData:
    # Replace missing values with zeros and collect the available years:
    nataccData[i].fillna(0, inplace = True)
    yearsAvailable = [year for year in nataccData[i].columns.tolist() if year.isdigit() and int(year)<=baseYear]
    for year in yearsAvailable:
        if year not in fullPeriod and int(year)<= baseYear:
            fullPeriod.append(year)
        
    # Rename price variables to a shorter format:
    if "Information" in nataccData[i].columns:
        nataccData[i].replace({"Current prices": "CP",
                               "At year 2010 prices": "FP_2010",
                               "Ar previous year's prices":"FP_prev_yr", # Note StatFin typo! Is it still there?
                               "At year 2016 prices": "2016_prices", 
                               "At year 2017 prices": "2017_prices"}, inplace = True)
        # Drop redundant info:
        nataccData[i].drop(nataccData[i][nataccData[i].Information.isin(["Changes in volume indices, %",
                                                                          "Proportion of transaction, %",
                                                                          "Ratio to GDP, %"])].index, inplace=True)
        
    # Fix another typo in the Statistics Finland data if it still exists:
    if "Sector:" in nataccData[i].columns:
        nataccData[i].rename(columns = {"Sector:": "Sector"}, inplace = True)
    
    # For all the columns listed below, shorten data names to only include the matching national accounting codes.
    # E.g. "011_016 Agriculture" becomes "011_016".
    for col in nataccData[i]:
        if col in ["Industry", "Sector", "Transaction", "Asset", "Type"]:
            nataccData[i][col] = nataccData[i][col].apply(lambda x: x.split(" ")[0]) 
            
        if col == "Industry":
            inds = nataccData[i].Industry.unique()
            
            # Fix some StatFin inconsistencies:
            # In some datasets industries are referred to with their aggregate letters, but we want only the 
            # number code format!
            if "D" in inds and not "35" in inds:
                nataccData[i].replace({"D": "35"}, inplace = True)           
            if "T" in inds and not "97_98" in inds:
                nataccData[i].replace({"T": "97_98"}, inplace = True)            
            
            # Now, drop those entries that start with a letter (= redundant industry aggregates)
            hasLetters = [x for x in inds if not x[0].isdigit()]
            nataccData[i].drop(nataccData[i][nataccData[i].Industry.isin(hasLetters)].index, inplace=True)
            # And rename the rest following the model naming convention: "011_016" becomes "I_011_016" etc.
            nataccData[i][col] = nataccData[i][col].apply(lambda x: "{}{}".format("I_", x))
        
        # Drop extra years (those more recent than our baseYear)
        try:
            yearNum = int(col)
            if yearNum>baseYear:
                nataccData[i].drop(col, axis = 1, inplace = True)
        except:
            pass


#%%
# View the list of available industries on the NATACC level:
set(nataccData['Capital formation'].Industry)


#%%
# And select manually a set of industires without overlapping entries:
nataccIndustries = [
"I_01", "I_02", "I_03", "I_05_06", "I_07", "I_08", "I_09", "I_10_12", "I_13_15", "I_16", "I_17", "I_18", "I_19", "I_20",
"I_21", "I_22", "I_23", "I_24", "I_25", "I_26", "I_27", "I_28", "I_29", "I_30", "I_31", "I_32", "I_33", "I_35",
"I_36", "I_37", "I_38", "I_39", "I_41+432_439", "I_42+431", "I_45", "I_46", "I_47", "I_49", "I_50", "I_51", "I_52", "I_53",
"I_55", "I_56", "I_58", "I_59_60", "I_61", "I_62_63", "I_64", "I_65", "I_66", "I_68201_68202", "I_681+68209+683",
"I_69", "I_70", "I_71", "I_72", "I_73", "I_74", "I_75", "I_77", "I_78", "I_79", "I_80", "I_81", "I_82", "I_841_842",
"I_843", "I_844", "I_845", "I_846", "I_85", "I_86", "I_87_88", "I_90_91", "I_92", "I_93", "I_94", "I_95", "I_96", "I_97_98"]


#%%
# Check that each dataset in nataccData contains all of the industries specified above:
for table in nataccData:
    if "Industry" in nataccData[table].columns:
        check = set(nataccIndustries).issubset(nataccData[table].Industry.unique())
        if check:
            print(check, table)
        
        else:
            for ind in nataccIndustries:
                if ind not in nataccData[table].Industry.unique():
                    print("Missing", ind, "in", table)


#%%
# Filter out redundant industry aggregates and rename some annoyingly long industry names:
renames = {"I_41+432_439": "I_41",
           "I_42+431": "I_42_43",
           "I_681+68209+683": "I_68",
           "I_68201_68202":"I_68A", 
           }

for table in nataccData:
    if "Industry" in nataccData[table].columns:
        nataccData[table] = nataccData[table][nataccData[table].Industry.isin(nataccIndustries)]
        nataccData[table] = nataccData[table].replace(renames)

# Also rename the entries listed in nataccIndustries:
nataccInd = [renames[i] if i in renames.keys() else i for i in nataccIndustries]


#%%
# if I_68202 comes before I_68, replace their order to match the input-output data:
if nataccInd.index("I_68A") < nataccInd.index("I_68"):
    a, b = nataccInd.index('I_68A'), nataccInd.index('I_68')
    nataccInd[b], nataccInd[a] = nataccInd[a], nataccInd[b]
    print("Swapped places for industries 68A and 68")
else:
    print("No changes made")


#%%
# Create a mapping from the ~80 national accounts industries to the 30 industries available in regional accounts:
natacc2reg = imf.mapperFunction(nataccInd, IND)


#%%
# Then, aggregate the industry dimension according to the mapping specified above.
# First, store the original data for error checking:
nataccDataOLD = nataccData.copy()
for i in nataccData:
    if "Industry" in nataccData[i].columns:
        nataccData[i].sort_values(["Industry"], inplace = True)
        nataccData[i]["IND"] = nataccData[i]["Industry"].map(natacc2reg)
        
        groupCols = list(nataccData[i].columns)
        groupCols = [x for x in groupCols if not x.isdigit() and x != "Industry"] 
        nataccData[i] = nataccData[i].groupby(groupCols, sort = False, as_index = False).sum().set_index("IND").reset_index()


#%%
# Check that annual totals still match after aggregation:
for data in [key for key in nataccData.keys() if key != "Employment"]:    
    for price in set(nataccData[data].Information):
        new = nataccData[data][nataccData[data]["Information"] == price][fullPeriod].sum()
        old = nataccDataOLD[data][nataccDataOLD[data]["Information"] == price][fullPeriod].sum()
        if np.allclose(new, old):
            print("OK for", data, price)

#%% [markdown]
# ### Query data on taxes and tax-like payments:

#%%
urlDict = {
"Taxes": "jul/vermak/statfin_vermak_pxt_127f.px"}

dgf.getData(urlDict, filters = {"Tiedot": ["cp"]}, active=True)


#%%
# Read in data:
taxData = {k: pd.read_csv(rawFolder+"/"+str(k)+"_Rawdata.csv",encoding="latin1",na_values =".") for k in urlDict.keys()} 

# And clean data:
for i in taxData:
    taxData[i].fillna(0, inplace = True)
        
    # Shorten the names of following variable values:
   # if "Data" in taxData[i].columns:
   #     taxData[i].replace({"Current prices": "CP", 
   #                         "Ratio to GDP, %": "GDPratio",
   #                         "Share of the sectors' total taxes, %": "ShrOfSectorTotal",
   #                         "Per capita, EUR": "eurPerCap"}, inplace = True)
    
    #if "Data" in taxData[i].columns:
    #    taxData[i].replace({"Current prices": "CP"}, inplace = True)

    # Rename government sectors: "S1311 Central government" becomes "S1311" etc.
    for col in taxData[i]:
        if col == "Sector":
            taxData[i][col] = taxData[i][col].apply(lambda x: x.split(" ")[0])          

#%%
# Last, we only need the current price data, so drop everything else:
govTaxlike = taxData["Taxes"].copy()
#govTaxlike = govTaxlike[govTaxlike["Data"] == "CP"].reset_index(drop = True)

#Rename columns
#Example: From '2018 Current prices, millions of euro' TO '2018'
for i in range(2,len(govTaxlike.keys()),1):
    n=govTaxlike.keys()[i][0:4]
    govTaxlike.rename(columns={govTaxlike.keys()[i]:n}, inplace=True)

   
#%% [markdown]
# ### Compile needed sources from different data tables:
# (datacheck.tab in the old database process, VATT-mallien-seloste.docx)

#%%
# From national capital stock data:
filter1 = "Consumption and retirement"
filter2 = "Capital formation"
NCP  = nataccData[filter1][(nataccData[filter1]["Type"]=="N") & (nataccData[filter1]["Information"]=="CP")]
NFP0 = nataccData[filter1][(nataccData[filter1]["Type"]=="N") & (nataccData[filter1]["Information"]=="FP_2010")]
DCP  = nataccData[filter1][(nataccData[filter1]["Type"]=="P51CK") & (nataccData[filter1]["Information"]=="CP")]
DFP0 = nataccData[filter1][(nataccData[filter1]["Type"]=="P51CK") & (nataccData[filter1]["Information"]=="FP_2010")]
ICP  = nataccData[filter2][nataccData[filter2]["Information"]=="CP"]
IFP  = nataccData[filter2][nataccData[filter2]["Information"]=="FP_2010"]

# From production account data:
filter3 = "Production accounts"
D2CP = nataccData[filter3][(nataccData[filter3]["Transaction"]=="P51CK")& (nataccData[filter3]["Information"]=="CP")]
OSCP = nataccData[filter3][(nataccData[filter3]["Transaction"]=="B2NT") & (nataccData[filter3]["Information"]=="CP")]
MICP = nataccData[filter3][(nataccData[filter3]["Transaction"]=="B3NT") & (nataccData[filter3]["Information"]=="CP")]


#%%
capData = {
"NCP":  NCP.copy(),  # Net capital stock, CP
"NFP0": NFP0.copy(), # Net capital stock, FP
"DCP":  DCP.copy(),  # Depreciation CP (NC, from capital accounts)
"D2CP": D2CP.copy(), # Depriciation CP (SURP, from production accounts)
"DFP0": DFP0.copy(), # Depriciation FP
"ICP":  ICP.copy(),  # Investment CP
"IFP0": IFP.copy(),  # Investment FP
"OSCP": OSCP.copy(), # Operating surplus, net
"MICP": MICP.copy(), # Mixed income, net
}


#%%
# Set "IND" to index for all tables in capData.
# Also, for now, drop I_97_98 from all tables because it contains only zero values
# and causes problems when calculating trends.
for table in capData:
    capData[table].set_index("IND", inplace = True)
    capData[table].drop("I_97_98", inplace = True)
    
    # Last, drop redundant columns:
    for redundant in ["Sector", "Transaction", "Information", "Asset", "Type"]:
        if redundant in capData[table]:
            capData[table].drop(redundant, axis = 1, inplace = True)


#%%
# Calculate baseyear depreciation rate: first an industry-specific value DEPR and a national aggregate DEPRNAT
capData["DEPR"] = (capData["DCP"][str(baseYear)] / capData["NCP"][str(baseYear)]).fillna(0)
capData["DEPRNAT"] = (capData["DCP"][str(baseYear)].sum() / capData["NCP"][str(baseYear)].sum())

#%% [markdown]
# ### Calculate industry-specific capital stock growth trends
# (trend.tab in the old database process, creates trend.har)

#%%
trend = {}
trend["NFP0"] = capData["NFP0"].copy()


#%%
# Check that there are no zero values in capital stocks data NFP0.
# If so, set a minimum value of 0.5 for calculating percentage change trends.
flag = True
for row in fullPeriod:
    for col in IND[:-1]:
        if trend["NFP0"].loc[col][row] == 0:
            flag = False
            trend["NFP0"].loc[row][col] = 0.5
            print(row, col, "set from zero to 0.5!")
if flag:
    print("No adjustments made.")


#%%
# Define some time periods:
fyear = fullPeriod[0]      # Capital data first year
lyear = fullPeriod[1:]     # All but first year
year_tr = fullPeriod[-11:] # Chosen trend period: last 10 years
numYear_tr = len(year_tr)  # Length of chosen period
preYear = fullPeriod[:-1]  # All but last year
preYear_tr = [str(int(year_tr[0])-1)] + year_tr # Trend period + 1 preceding year for calculating annual changes
capIND = IND[:-1]          # Household service activities omitted from capital trend calulations (empty data)


#%%
# Estimate capital stock data (stock + investment - depreciation) and compare to the reported StatFin values.

# Estimate:
trend["NFP0_est"] = pd.DataFrame(0.0, index = capIND, columns = lyear)
for year in lyear:
    annualCol = trend["NFP0"][str(int(year)-1)] + capData["IFP0"][year] - capData["DFP0"][year]
    trend["NFP0_est"][year] = annualCol
    
# Actual data:
trend["NFP0_data"] = trend["NFP0"][lyear].copy()

# Nominal difference between original and estimated data:
capDiagnostics = {}
capDiagnostics["NFP0_chk"] = trend["NFP0_data"] - trend["NFP0_est"]

# Change rate between original and estimated data
trend["DEVK"] = 100 * ((trend["NFP0_est"][year_tr] - trend["NFP0_data"][year_tr]) / trend["NFP0_data"][year_tr]).fillna(0)


#%%
# Add first year back to data and sort:
trend["NFP0_est2"] = trend["NFP0_est"].copy()
trend["NFP0_est2"][fyear] = trend["NFP0"][fyear]
trend["NFP0_est2"].sort_index(axis=1, inplace = True)


#%%
# Annual changes between years:

# Initialize empty matrices:
trend["AG0_est"] = pd.DataFrame(0.0, index = capIND, columns = lyear) # Annual growth by estimated data
trend["AG0_data"]= pd.DataFrame(0.0, index = capIND, columns = lyear) # Annual growth by original data

for year in lyear:
    annualColEst = 100 * ((trend["NFP0_est"][year] / trend["NFP0_est2"][str(int(year)-1)]) -1).fillna(0)
    trend["AG0_est"][year] = annualColEst
    
    annualColData = 100 * ((trend["NFP0_data"][year] /  trend["NFP0"][str(int(year)-1)]) -1).fillna(0)
    trend["AG0_data"][year] = annualColData


#%%
# Sum trends for trend period year_tr:
trend["AG0_est2"] = trend["AG0_est"][year_tr]
trend["AG0_data2"]= trend["AG0_data"][year_tr]

trend["TRNK_est"] = pd.DataFrame(100 * ((1 + trend["AG0_est2"]/100).product(axis = 1)  ** (1/numYear_tr) -1))
trend["TRNK_data"]= pd.DataFrame(100 * ((1 + trend["AG0_data2"]/100).product(axis = 1) ** (1/numYear_tr) -1))

# trend.tab ja trend.har valmiit tässä

#%% [markdown]
# ### Add more parameters to data
# (fixdata.tab in the old database process, creates CAP2.har and WORKFORCE.har)

#%%
fixData = {}


#%%
# Operating surplus from StatFin data is in net value, so it excludes depreciation of capital.
# It must be added back in:

# First, check that the size of all dataframes is identical, before making any additions
capData["OSCP"].shape == capData["D2CP"].shape == capData["MICP"].shape


#%%
#capData["OSCP_B"] = capData["OSCP"].copy()                             # capData["OSCP] = original data
fixData["OSCP"] = capData["OSCP"] + capData["D2CP"] + capData["MICP"]  # Add depreciation and mixed income
fixData["OSCP2"]= capData["OSCP"] + capData["D2CP"]                    # Add depreciation only


#%%
# Next, choose 4 additional time periods ending to the baseYear and create capital trends:
additionalTrends = {
# Trend start year
"trend1": "1975",
"trend2": "1990",
"trend3": "2000",
"trend4": "2010"}

for period in additionalTrends.values():
    fixData["trend_"+period] = pd.DataFrame(((capData["NCP"][str(baseYear)] / capData["NCP"][period]) ** (1/(baseYear - int(period)))).fillna(0))


#%%
# Calculate estimated value for the net capital stock NCP:
fixData["NCP_est"] = pd.DataFrame(0.0, index = capIND, columns = lyear)
for year in lyear:
    annualCol = capData["NCP"][str(int(year)-1)] + capData["ICP"][year] - capData["DCP"][year]
    fixData["NCP_est"][year] = annualCol


#%%
# From data: net capital stock, current values
fixData["NFP0L"] = capData["NFP0"][lyear].copy()
fixData["DEVK"] = 100 * ((trend["NFP0_est"] - trend["NFP0"][lyear])/trend["NFP0"][lyear]).fillna(0)


#%%
# Depreciation rate (this time year-to-year):
fixData["DEPR"] = pd.DataFrame(0.0, index = capIND, columns = lyear)
for year in lyear:
    annualCol = (capData["DFP0"][str(int(year)-1)] / capData["NFP0"][year] ).fillna(0)
    fixData["DEPR"][year] = annualCol


#%%
# CHECK FOR FOLLOWING CONDITIONS:

# There might be new industries with some operating surplus or depreciation
# but no capital stock. Check that these do not exist (all indusries have 
# non-zero capital stock for all years.)

# Checking that all values for all years are non-zero:
print("Check operating surplus:", all(fixData["OSCP"] > 0))
print("Check operating surplus (without mixed income):", all(fixData["OSCP2"] > 0) )
print("Check depreciation rate:", all(capData["DCP"] > 0))
print("Check net capital stock:", all(capData["NCP"] > 0))

#%% [markdown]
# #### Calculate rates of  return for capital
# 
# The model allows for two different RORs:
# * RORN -> Normal (historical) ROR, calculated from data.
# * ROR_se -> Static expectations ROR (Investors consider only current rentals and asset prices when forming expectations about rates of return).
# 
# Further, the ROR is calculated for two different cases: with and without operating surplus.

#%%
# First, calculate VCAP_AT_TM, that is, the average capital stock between the beginning and end of the year:
fixData["VCAP_AT_TM"] = pd.DataFrame(0, index = capIND, columns=lyear)
for year in lyear:
    annualCol = 0.5 * ((capData["NCP"][str(int(year)-1)] + capData["NCP"][year]).fillna(0))
    fixData["VCAP_AT_TM"][year] = annualCol
    
# Gross operating surplus, current prices:
fixData["RQK"] = 100 * ((fixData["OSCP"] - capData["DCP"]) / capData["NCP"])


#%%
# Then, query consumer price index (CPI) data from Statistics Finland:
urlDict = {"CPI": "/hin/khi/statfinpas_khi_pxt_006_201904.px"}
# 006 -- Consumer Price Indices, overall index
dgf.getData(urlDict)


#%%
# Read in CPI data:
cpiData = {k: pd.read_csv(rawFolder+"/"+str(k)+"_Rawdata.csv",encoding="utf-8",na_values =".") for k in urlDict.keys()} 

# And check the available index base years:
[data for data in cpiData["CPI"].columns.unique() if "100" in data]


#%%
# Choose the base year, and clean the dataset.
# Note: the period must be long enough to include the user-specified trend period leading to baseYear (here 10 years)
infBase = "CPI 2000=100 Point figure"

# Drop redundant columns:
cpiData["CPI"] = cpiData["CPI"][["Year", "Month", infBase]]

# Only include the values for "Annual average", dropping all the month-to-month entries.
# This also drops all the NAN values, that is, data older than the chosen infBase.
cpiData["CPI"] = cpiData["CPI"][cpiData["CPI"]["Month"] == "Annual average"].dropna()

# Finish up the cleaning:
cpiData["CPI"].set_index("Year", inplace = True)
cpiData["CPI"].drop("Month", axis=1, inplace = True)
cpiData["CPI"].rename(columns = {infBase: "CPI_LEV"}, inplace = True)
cpiData["CPI"] = cpiData["CPI"].reindex([int(year) for year in preYear_tr])


#%%
# Get the lagged values:
fixData["LEV_CPI"] = cpiData["CPI"].copy()

# Original value:
fixData["LEV_CPI"] /= 100
# Once lagged:
fixData["LEV_CPI_L"] = fixData["LEV_CPI"][:-1]
fixData["LEV_CPI_L"].index += 1 
# Double lagged:
fixData["LEV_CPI_2L"] = fixData["LEV_CPI_L"][:-1]
fixData["LEV_CPI_2L"].index += 1 


#%%
# Get inflation rate from consumer price index:
fixData["INF"] = fixData["LEV_CPI"].pct_change().dropna()
# Real interest rate: KORJAA TÄHÄN VUOSITTAINEN LUKU!!
fixData["RINT"] = pd.DataFrame(0.02, index = year_tr, columns = ["RINT"])
# Nominal interest rate
fixData["INT"] = ((fixData["RINT"] + 1).multiply((1+fixData["INF"].values), axis = 0) -1).rename(columns = {"RINT":"INT"})
# Fix the interest rate dataframe index to string format:
fixData["INT"].index = fixData["INT"].index.map(int)


#%%
# Next, calculate the capital income tax rate by deviding annual duty on interest by the operating surplus value
# -> jaa korkotulotulojen lähdeveron vuosittainen kertymä (Tilastokeskuksen aineistot) 
# toimintaylijäämän arvolla koko kansantalouden tasolla. 

# First, filter out the current-priced duty on interests for the whole economy:
#fixData["TAXK"] = govTaxlike[(govTaxlike["Tax category"] == "-1000 Duty on interests") & (govTaxlike["Sector"] == "S13") & (govTaxlike["Data"] == "CP")].copy()
#fixData["TAXK"] = govTaxlike[(govTaxlike["Tax category"] == "-1000 Duty on interests") & (govTaxlike["Sector"] == "S13")].copy()
fixData["TAXK"] = govTaxlike[(govTaxlike["Tax category"] == "110001 Duty on interests") & (govTaxlike["Sector"] == "S13")].copy()
# Transpose data to suitable form and rename the column:
fixData["TAXK"] = fixData["TAXK"][[year for year in year_tr]].transpose().rename_axis('Year', axis=1)
fixData["TAXK"].rename(columns={fixData["TAXK"].columns[0]: "TAX_CAP" }, inplace = True)

# Last, divide with operating surplus to get the tax rate:
fixData["TAX_K_RATE"] = fixData["TAXK"].div(fixData["TAXK"].add(fixData["OSCP"][year_tr].sum(), axis = 0), axis = 0) * 100


#%%
# Post-tax real interest rate, static expectations:
fixData["RINT_PT_SE"] = ((1 + fixData["INT"].multiply((1-fixData["TAX_K_RATE"].values),                        axis=0)).div((1+fixData["INF"].values), axis=0) -1).rename(columns = {"INT": "RINT_PT_SE"})


#%%
# Base year CPI and inflation values: (normal, lagged, double lagged)
fixData["LEV_CPI_B"]    = fixData["LEV_CPI"].loc[baseYear].copy()
fixData["LEV_CPI_L_B"]  = fixData["LEV_CPI_L"].loc[baseYear].copy()
fixData["LEV_CPI_2L_B"] = fixData["LEV_CPI_2L"].loc[baseYear].copy()
fixData["INF_B"] = fixData["INF"].loc[baseYear].copy()
fixData["INT_B"] = fixData["INT"].loc[baseYear].copy()


#%%
# Static expectations rate of return:
# ROR  = no mixed income
# ROR2 = yes mixed income

fixData["ROR_SE"] = (1/(1+ float(fixData["RINT_PT_SE"].loc[baseYear]))) *( (fixData["OSCP"][lyear] * (1-float(fixData["TAX_K_RATE"].loc[str(baseYear)]))).div(fixData["VCAP_AT_TM"], axis = 0).add((1-fixData["DEPR"]), axis =0) )-1

fixData["ROR_SE2"] = (1/(1+ float(fixData["RINT_PT_SE"].loc[baseYear]))) *( (fixData["OSCP2"][lyear] * (1-float(fixData["TAX_K_RATE"].loc[str(baseYear)]))).div(fixData["VCAP_AT_TM"], axis = 0).add((1-fixData["DEPR"]), axis =0) )-1


#%%
# Investment to capital ratio:
fixData["IKRT"] = (capData["ICP"][lyear] / capData["NCP"][lyear]).fillna(0)

#%% [markdown]
# #### Labor part
# 
# Combines information from national accounts data and labour force survey data to produce an initial employment value of 1 for baseYear.

#%%
empData = {}


#%%
# Query regional labour force survey data from Statistics Finland:
urlDict = {
"Labour force survey": "tym/tyti/vv/statfin_tyti_pxt_11pn.px"}

dgf.getData(urlDict, active=True)


#%%
# Read in data:
surveyData = {k: pd.read_csv(rawFolder+"/"+str(k)+"_Rawdata.csv",encoding="ISO-8859-1",na_values =".") for k in urlDict.keys()}


#%%
# Clean data:
for i in surveyData:
    surveyData[i].fillna(0, inplace = True)
    
    # Rename:
    surveyData[i].rename(columns = {"Region 2011": "Region",
                                    "Population, 1000 persons": "WA_POP",
                                    "Active population (employed and unemployed in total), 1000 persons": "LAB_SUP",
                                    "Employed, 1000 persons": "EMP",
                                    "Unemployed, 1000 persons": "UNEMP"}, inplace = True)
    
    # Drop redundant columns:
    for redundant in ["Activity rate, %", "Employment rate, %", "Unemployment rate, %"]:
        if redundant in surveyData[i].columns:
            surveyData[i].drop(redundant, axis = 1, inplace = True)


#%%
# Drop the regional dimension, it is not needed here:
empData["wfData"] = surveyData["Labour force survey"][surveyData["Labour force survey"]["Region"] == "WHOLE COUNTRY"].set_index("Year").drop("Region", axis = 1)


#%%
# Then, filter out labour data from the annual national accounts:
# E1 = Employment, 1000 persons
empData["employ_i"] = nataccData["Employment"][nataccData["Employment"]["Transaction"] == "E1"].set_index("IND").drop(["Sector", "Transaction"], axis = 1).sum()


#%%
# Get a list of years for which data are available both for national accounts and labour survey:
empData["years"] = [year for year in empData["employ_i"].index if year in empData["wfData"].index.astype("str")]


#%%
# Reindex data using the list of common years:
empData["wfData1"] = empData["wfData"].reindex([int(yr) for yr in empData["years"]]).copy()
empData["wfData2"] = empData["wfData"].reindex([int(yr) for yr in empData["years"]]).copy() # Data edited using natacc emp 
empData["employ_i"] = empData["employ_i"].reindex(empData["years"])

empData["wfData2"]["EMP"] = empData["employ_i"].values
empData["wfData2"]["UNEMP"] = empData["wfData2"]["LAB_SUP"] -  empData["wfData2"]["EMP"] 

empData["wfInit"] = empData["wfData2"] / empData["wfData2"].loc[baseYear]["EMP"] # data initial emp 1 at baseyear
empData["wfInit2"] = empData["wfData1"]/ empData["wfData1"].loc[baseYear]["EMP"] # data initial emp 1 at baseyear


#%%
fixData["EMPLOYMENT"] = empData["wfInit"].loc[baseYear]["EMP"]
fixData["LAB_SUP"] = empData["wfInit"].loc[baseYear]["LAB_SUP"]

#%% [markdown]
# ### Data adjusting
# 
# * Ensure that the capital data created above matches with the input-output data created in the ORANI-G steps.
# * Industry-specific depreciation rates and RORs are assigned a maximum value of 20%.
# * Create EXTRA.har files
# 
# (adjustdata.tab in the 2008 data creation process, creates dataout.har and extout.har)

#%%
# Initialize empty dictionary to store data:
adjust = {}
check  = {}


#%%
# Read in some data arrays from base data:
V1LAB = pd.DataFrame(baseData.getHeaderArrayObj("1LAB")["array"], index = IND, columns = OCC)
V1CAP = pd.Series(baseData.getHeaderArrayObj("1CAP")["array"], index = IND)
V1OCT = pd.Series(baseData.getHeaderArrayObj("1OCT")["array"], index = IND)

V2BAS_S = pd.DataFrame(baseData.getHeaderArrayObj("2BAS")["array"].sum(axis=1), index = COM, columns = IND)
V2TAX_S = pd.DataFrame(baseData.getHeaderArrayObj("2TAX")["array"].sum(axis=1), index = COM, columns = IND)
V2MAR_SM = pd.DataFrame(baseData.getHeaderArrayObj("2MAR")["array"].sum(axis=1).sum(axis=2), index = COM, columns = IND)

V2PUR_S = V2BAS_S + V2TAX_S + V2MAR_SM
V2TOT   = V2PUR_S.sum()


# Redundant?
#V2BAS_CS  = pd.Series(baseData.getHeaderArrayObj("2BAS")["array"].sum(axis=1).sum(axis=0), index = IND)
#V2TAX_CS  = pd.Series(baseData.getHeaderArrayObj("2TAX")["array"].sum(axis=1).sum(axis=0), index = IND)
#V2MAR_CSM = pd.Series(baseData.getHeaderArrayObj("2MAR")["array"].sum(axis=0).sum(axis=0).sum(axis=1), index = IND)
# This should be identical to header "2TOT" in ../oranig2013/summary.har:
#V2TOT_CS  = V2BAS_CS + V2TAX_CS + V2MAR_CSM

for table in [V1CAP, V1OCT, V2TOT]:
    table.drop("I_97_98", inplace = True)

#%% [markdown]
# #### Baseyear reference values

#%%
# Normalize asset price of capital for all industries in baseYear to 1:

# Asset price of capital stocks, start of forecast year 
adjust["PCAP_AT_T"] = pd.Series(1.0, index = capIND)

# Asset price of capital by industry, year average
adjust["PCAP_I"] = pd.Series(1.0, index = capIND)

# Start of year capital stocks valued at start start of year prices
adjust["VCAP_AT_T"] = capData["NCP"][str(baseYear-1)]


#%%
# Baseyear expected real interest rate (?)
adjust["RINT_PT_SE"] = float(fixData["RINT_PT_SE"].loc[baseYear])

# Baseyear capital income tax rate
adjust["TAX_K_RATE"] = float(fixData["TAX_K_RATE"].loc[str(baseYear)])


#%%
# Depreciation rate of capital stock in ind i in baseYear:
adjust["DEPnew"] = capData["DCP"][str(baseYear)] / adjust["VCAP_AT_T"]

# Average depreciation rate (industry-specific):
adjust["DEPave1"] = capData["DCP"][fullPeriod].sum(axis=1) / capData["NCP"][fullPeriod].sum(axis=1)

# Average depreciation rate (aggregate):
adjust["DEPave2"] = adjust["DEPave1"].sum() / len(adjust["DEPave1"].index)


#%%
# Replace zero depreciation rates, if they exist, with long run averages:
flag = True
for ind in adjust["DEPnew"].index:
    if adjust["DEPnew"].loc[ind] == 0.0:
        flag = False
        adjust["DEPnew"].loc[ind] = adjust["DEPave2"]
        print("Set", ind, "depreciation rate from zero to long run average value", adjust["DEPave2"])
if flag:
    print("OK! No adjustments needed.")

#%% [markdown]
# #### Set maximum level for depreciation rates

#%%
# Cap maximum depreciation rate:
maxdep = 0.2
flag = True
for ind in adjust["DEPnew"].index:
    if adjust["DEPnew"].loc[ind] > maxdep:
        flag = False
        orig = adjust["DEPnew"].loc[ind]
        adjust["DEPnew"].loc[ind] = maxdep
        print("Capped", ind, "depreciation rate from", orig, "to", maxdep)
if flag:
    print("OK! No adjustments needed.")

#%% [markdown]
# #### (Jos toimintaylijäämä siirretään V1CAP -> V1LAB, tee se tässä!)
# ks. vanha ainestovaihe CAPITAL/adjustdata.tab rivi 377.
#%% [markdown]
# #### Set maximum level for rates of return

#%%
# Value of capital, baseYear in mid-year prices:
adjust["VCAP_AT_TM"] = adjust["VCAP_AT_T"] * adjust["PCAP_I"] / adjust["PCAP_AT_T"]


#%%
# Static expectations ROR:
adjust["ROR_SE"] = (1 / (1 + adjust["RINT_PT_SE"])) *((V1CAP * (1 - adjust["TAX_K_RATE"])) / adjust["VCAP_AT_TM"] + (1 - adjust["DEPnew"])) - 1


#%%
adjust["ROR_SE20"] = adjust["ROR_SE"].copy()
maxror = 0.2
flag = True
for i in adjust["ROR_SE20"].index:
    if adjust["ROR_SE20"].loc[i] > maxror:
        flag = False
        adjust["ROR_SE20"].loc[i] = maxror
        print("Capped rate of return for", i, "to", maxror)
if flag:
    print("No adjustments made.")

#%% [markdown]
# #### Recalculate V1CAP using the adjusted values for depreciation and rates of return
# 
# Changes in V1CAP are transferred to other costs (V1OCT) to maintain database balance.
# 
# The idea is that we are moving "pure profits" to a non-resource using area !

#%%
# Calculate new V1CAP
adjust["V1CAPnew"]=adjust["VCAP_AT_TM"] * ((1 + adjust["RINT_PT_SE"])*(1+adjust["ROR_SE20"])-(1-adjust["DEPnew"])) /                   (1-adjust["TAX_K_RATE"])
    
adjust["ROR_SEnew"] = (1 / (1 + adjust["RINT_PT_SE"])) *(    (adjust["V1CAPnew"] * (1 - adjust["TAX_K_RATE"]) )/adjust["VCAP_AT_TM"] + (1-adjust["DEPnew"])     ) -1


#%%
# Difference between new and old values:
V1CAPdiff = adjust["V1CAPnew"] - V1CAP 

# Redistribute the difference to other cost tickets:
V1CAP += V1CAPdiff
V1OCT -= V1CAPdiff


#%%
# Read nominal investment:
check["Invest"] = capData["ICP"][str(baseYear)]


#%%
# Baseyear capital growth rate:
adjust["K_GR"] = V2TOT / adjust["VCAP_AT_T"] - adjust["DEPnew"]

# 10-year trend growth rate (industry-specific):
adjust["TREND10yr"] = capData["NCP"][year_tr].T.pct_change().add(1).prod().pow(1.0/numYear_tr).sub(1)

# 10-year trend growth rate (aggregate):
adjust["TRENDNAT"] = capData["NCP"][year_tr].sum().pct_change().add(1).prod() ** (1.0/numYear_tr) -1


#%%
# Recip. of slopes of cap. supply curves when K_GR(i)=TREND_K(i)R:
adjust["SMURF"] = pd.Series(0.5, index = capIND)

# TREND_K = historically normal capital growth rate:
adjust["TREND_K"] = adjust["TREND10yr"].copy()

# Set a 10% limit for all industries between  maximum and trend growth rates.
# For minimum capital growth rates, negative depreciation rate is used.
DIFF = 0.1
adjust["K_GR_MAX"] = adjust["TREND_K"] + DIFF
adjust["K_GR_MIN"] =-adjust["DEPnew"] 


#%%
# Adjusting capital growth rate to some reasonable figures:
flag = True
for ind in adjust["K_GR"].index:
    value = adjust["K_GR"].loc[ind]
    if value > adjust["K_GR_MAX"].loc[ind]:
        flag = False
        adjust["K_GR"].loc[ind] = adjust["K_GR_MAX"].loc[ind]
        print("Capped", ind, "to the maximum value!")
    if value < adjust["K_GR_MIN"].loc[ind]:
        flag = False
        adjust["K_GR"].loc[ind] = adjust["K_GR_MIN"].loc[ind]
        print("Adjusted", ind, "to a minimum value!")
if flag:
    print("OK! No adjustments needed.")
if not flag:
    print("Adjust investments to account for the adjustments in capital growth rates! See adjustdata.tab row 582!")


#%%
# Check that the total investments still match:
V2TOTnew = adjust["VCAP_AT_T"]*(adjust["K_GR"] + adjust["DEPnew"])
all(abs(V2TOTnew - V2TOT) < 0.000001)


#%%
V2MULT = V2TOTnew / V2TOT


#%%
# Compute normal long-run rates of return that is not updated on the model baseline:

# Coefficient in capital supply curve
adjust["COEFF_SL"] = adjust["SMURF"] * (adjust["K_GR_MAX"] - adjust["K_GR_MIN"]) /                    ((adjust["K_GR_MAX"] - adjust["TREND_K"]) * (adjust["TREND_K"] - adjust["K_GR_MIN"]))


#%%
# Natural ROR:
adjust["RORNnew"] = adjust["ROR_SEnew"] - (1/adjust["COEFF_SL"]).fillna(1) *(  (np.log(adjust["K_GR"] - adjust["K_GR_MIN"]) - np.log(adjust["K_GR_MAX"] - adjust["K_GR"])) -(np.log(adjust["TREND_K"] - adjust["K_GR_MIN"]) - np.log(adjust["K_GR_MAX"] - adjust["TREND_K"]))  )

#%% [markdown]
# 
# #### Additional data for EXTRA.har files

#%%
# Vector shifter, equilibrium rate of return:
FSTA = pd.Series(0.0, index = IND)
# Industry soecific shifter in equilibrium rate of return:
FRRI = pd.Series(0.0, index = IND)
# Adjustment coefficient:
ADJC = pd.Series(0.5, index = IND)
# Control adjustment of RORs in forward-looking expectations algorithm
ADRE = pd.Series(0.05, index = IND)
# Time set:
FNUM = ["N"+str(x) for x in range(1,51)]
TIME = ["T"+str(x) for x in range(0,50)]
# Adjustment coefficient:
RORG = pd.DataFrame(0.0, index = IND, columns = FNUM)
# Level of consumer quantity:
LVX3 = pd.DataFrame(1.0, index = COM, columns = SRC)
# Share of consumer prices:
B3SH = pd.DataFrame(1.0, index = COM, columns = SRC)
# Level of consumer prices:
LVP3 = pd.DataFrame(1.0, index = COM, columns = SRC)


#%%
# EXTRA parameters:
extraParams = {
# coef. name: (value,  header, long name)
"DUM_YEAR1":   (1.0,   "0045", "Dummy for the first year"),
"BETA1":       (0.5,   "BTA1", "Parameter for soft government budget"),
"BETA2":       (1.5,   "BTA2", "Parameter for soft government budget"),
"LEV_CPI_L":   (1.0,   "CPIL", "Lagged level of consumer prices"),
"DEFDIFSUM":   (0.0,   "DDIF", "Cumulative diference to start-year deficit"),
"DEFDIFNPV":   (0.0,   "DDIV", "Capitalized cumulative difference to start-year deficit"),
"DISCFACT":    (1.0,   "DFAC", "Sum of discounting terms"),
"R_DEFGDP_BO": (0.0,   "DGPD", "Public sector debt as percentage from GDP"),
"DIFF":        (0.1,   "DIFF", "Maximum difference from trend rate growth"),
"FEMPADJ":     (0.0,   "EADJ", "Level of the shift variable in E_d_f_empadj"),
"f_eeqror":    (0.0,   "FCSE", "F_EEQROR"),
#"LEV_CPI":     (0.0,   "GREV", "Level of consumer prices"),
"NAIRU":       (0.07,  "NROU", "Natural rate of unemployment"),
"NATSAVSH":    (1.0,   "NSSH", "Share of national savings in GNP"),
"PLAB":        (1.035, "PLAB", "Nominal wage level"),
"PLAL":        (1.0,   "PLAL", "Nominal wage level, lagged"),
"PSDATTGP0":   (0.0,   "PSDG", "Public sector debt as percentage from GDP"),
"COMPRFAC":    (1.0,   "RFAC", "Compound interest rate from base year"),
"RINT":        (0.02,  "RINT", "Base year real interest rate"), # baseYear
"RALPH":       (0.0,   "RLPH", "Profit tax parameter"),
"RINT_L":      (0.01,  "RNTL", "Lagged real interest rate"),
"RWAGE":       (1.0,   "RWAG", "Real wage (=CPI deflated wage rate)"),
"YEAR":        (5.0,   "YEAR", "Year of RE SIM (??)"),
}


#%%
def addMissingInd(dictionary):
    for i in dictionary:
        data = dictionary[i]
        try:
            dataIndex = data.index.tolist()
            if dataIndex == capIND:
                dictionary[i] = data.reindex(IND).fillna(0)
        except:
            pass 


#%%
for d in [adjust, trend, fixData, capData]:
    addMissingInd(d)

#%% [markdown]
# #### Write data to HAR output files

#%%
extraDims = {
"IND": IND,
"COM": COM,
"TIME": TIME,
"FNUM": FNUM,
"SRC": SRC,
}


#%%
extOut={
#coefficient name: (dataname, header name, long name, [list of dimensions])
"VCAP_AT_T":  (adjust["VCAP_AT_T"], "VCAP", "Start of year capital stocks valued at start of year prices", ["IND"]),
"TREND10yr":  (adjust["TREND10yr"], "TRNK", "10-year trend growth", ["IND"]),   
"TRENDNAT" :  (adjust["TRENDNAT"], "TNAT", "10-year aggregate trend growth", []),  
"LEV_CPI_2L": (fixData["LEV_CPI_2L_B"], "LCP2", "Base year double lagged CPI", []),
"LEV_CPI_L":  (fixData["LEV_CPI_L_B"], "LCPL", "Base year lagged CPI", []),    
"LEV_CPI":    (fixData["LEV_CPI_B"], "LCPI", "Base year CPI", []),  
"F_EEQROR_I": (FSTA, "FSTA", "Vector shifter for EEQROR, equilibrium rate of return", ["IND"]),
"FRRI":       (FRRI, "FRRI", "Industry soecific shifter in equilibrium rate of return", ["IND"]),
"ADJC":       (ADJC, "ADJC", "Adjustment coefficient", ["IND"]),  
    
"PCAP_I_B":  (adjust["PCAP_I"], "PCAB", "Asset price of capital stock by ind at baseline, average in year", ["IND"]),
"PCAP_I":    (adjust["PCAP_I"], "PCAI", "Asset price of capital by industry, average in year", ["IND"]),
"PCAP_I_L":  (adjust["PCAP_I"], "PCAL", "Asset price of capital stocks, averange of year t-1, init solution", ["IND"]),
"PCAP":      (adjust["PCAP_I"], "PCAP", "Asset price of capital stocks, start of the forecast year", ["IND"]),    
"PCAT":      (adjust["PCAP_I"], "PCAT", "Asset price of capital stocks, end of the forecast year", ["IND"]),    

"DEPnew": (adjust["DEPnew"], "DEPR", "Depreciation of capital stock in industry i", ["IND"]),   
"RORNnew":(adjust["RORNnew"], "RORN", "Historically normal rate of return", ["IND"]),
"SMURF":  (adjust["SMURF"], "SMRF", "Recip. of slopes of cap. supply curves when K_GR(i) = TREND_K(i)", ["IND"]),
    
"EMPLOYMENT": (fixData["EMPLOYMENT"], "EMPL", "Aggregate employment 1 in initial solution for year t", []),    
"LAB_SUP":    (fixData["LAB_SUP"], "LSUP", "Aggregate labour supply for year t", []),    
    
"ADRE": (ADRE, "ADRE", "Control adjustment of RORs in forward-looking expectations algorithm", ["IND"]),
"RORG": (RORG, "RORG", "Adjustment coefficient", ["IND", "TIME"]),
    
"LVX3":   (LVX3, "LVX3", "Level of consumer quantity", ["COM", "SRC"]),
"LVSHR3": (B3SH, "B3SH", "Share of consumer prices", ["COM", "SRC"]),
"LVP3":   (LVP3, "LVP3", "Level of consumer prices", ["COM", "SRC"]),
}    


#%%
# Add the extra parameters:
for i in extraParams:
    coeff = i
    value = extraParams[i][0]
    header= extraParams[i][1]
    longname = extraParams[i][2]
    extOut[i] = (value, header, longname, [])


#%%
output = {**extraDims, **extOut}
hwf.data2har(output, extraDims).writeToDisk(harFolder+"/capitalextra.har")

#%% [markdown]
# #### Write the actual output capital.har

#%%
capDims = {
"IND": IND,
"COM": COM,
"SRC": SRC,
"YEAR": fullPeriod,
"YETR": year_tr,
"YERL": lyear,
"NIND": nataccInd,
}


#%%
capOut = {
#coefficient name: (dataname, header name, long name, [list of dimensions])
"LEV_CPI_B":    (fixData["LEV_CPI_B"], "LCPI", "Level of CPI, base year", []),
"LEV_CPI_L_B":  (fixData["LEV_CPI_L_B"], "LCPL", "Lagged level of CPI, base year" , []),
"LEV_CPI_2L_B": (fixData["LEV_CPI_2L_B"], "LCP2", "Double lagged level of CPI, base year", []),
    
"RINT":  (fixData["RINT"], "RINT", "Real interest rate", ["YETR"]),
"INF_B": (fixData["INF_B"], "INF", "Base year inflation", []),
"INT_B": (fixData["INT_B"], "INT", "Base year nominal interest rate", []),
    
"TAX_K_RATE": (fixData["TAX_K_RATE"], "TKRT", "Rate of tax on capital income", ["YETR"]),
"RINT_PT_SE": (fixData["RINT_PT_SE"], "RNTP", "Post-tax real interest rate, static expectations", ["YETR"]),
"EMPLOYMENT": (fixData["EMPLOYMENT"], "EMPL", "Aggregate employment, 1 in initial solution year", []),
"LAB_SUP":    (fixData["LAB_SUP"], "LSUP", "Aggregate labour supply", []),
    
"DCP": (capData["DCP"], "DCP", "Depreciation, current prices", ["IND", "YEAR"]),
"NCP": (capData["NCP"], "NCP", "Net capital stock current prices", ["IND", "YEAR"]),
    
"TREND75": (fixData["trend_1975"], "TR75", "Trend growth in capital stock", ["IND"]),
"TREND90": (fixData["trend_1990"], "TR90", "Trend growth in capital stock", ["IND"]),
"TREND00": (fixData["trend_2000"], "TR00", "Trend growth in capital stock", ["IND"]),
"TREND10": (fixData["trend_2010"], "TR10", "Trend growth in capital stock", ["IND"]),
    
"NFP_est": (trend["NFP0_est"], "NFPE", "Net capital stock, estimated", ["IND", "YERL"]),
"NFP0L":   (trend["NFP0"][lyear], "NFPL", "Net capital stock, current prices", ["IND", "YERL"]),
"NFP0":    (trend["NFP0"], "NFP0", "Net capital stock, fixed prices", ["IND", "YEAR"]),
"DEVK":    (fixData["DEVK"], "DEVK", "Net capital stock difference", ["IND", "YERL"]),
"DEPR":    (fixData["DEPR"], "DEPR", "Depreciation rate", ["IND", "YERL"]),
    
"RQK":(fixData["RQK"], "RQK", "Gross operating surplus, current prices", ["IND", "YEAR"]),
"DEP":(adjust["DEPnew"], "DEP", "Base year depriciation rate", ["IND"]),   # Onko oikea DEP?
    
"ROR_SE":    (fixData["ROR_SE"], "ROR", "Rate of return, static expectations", ["IND", "YERL"]),
"ROR_SE2":   (fixData["ROR_SE2"], "ROR2", "Rate of return, static expectations incl mixed income", ["IND", "YERL"]),
"VCAP_AT_TM":(fixData["VCAP_AT_TM"], "VCPM", "Value of capital, start of fcast year in mid-yr prices", ["IND", "YERL"]),
"IKratio":   (fixData["IKRT"], "IKRT", "Investment to capital ratio", ["IND", "YERL"]),
    
"OSCP":(fixData["OSCP"], "OSCP", "Operating surplus", ["IND", "YEAR"]),
"D2CP":(capData["D2CP"], "D2CP", "Depreciation, current prices, from production accounts", ["IND", "YEAR"]),
"MICP":(capData["MICP"], "MICP", "Mixed income", ["IND", "YEAR"]),
"NCP_est":(fixData["NCP_est"], "NCPE", "Net capial stock, estimate, current prices", ["IND", "YERL"]),
"ICP":(capData["ICP"], "ICP", "Investment, current prices", ["IND", "YEAR"]),
"OSCP2":(fixData["OSCP2"], "OSC2", "Operating surplus without mixed income", ["IND", "YEAR"]),

}


#%%
output = {**capDims, **capOut}
hwf.data2har(output, capDims).writeToDisk(harFolder+"/capital.har")


#%%
# Write out updated headers for V1CAP and other cost tickets.
# Also add the missing industry I_97 that was omitted from capital calculations.
# Check if V1LAB and V2*** should also be recalculated (adjustdata.tab)
V1CAP = V1CAP.reindex(IND).fillna(0)
V1OCT = V1OCT.reindex(IND).fillna(0)


#%%
dataAdjustment = {
"1CAP": (V1CAP, "1CAP", "Cost of capital NEW", ["IND"]),
"1OCT": (V1OCT, "1OCT", "Other cost tickets NEW", ["IND"])
}


#%%
hwf.data2har(dataAdjustment, {"IND": IND}).writeToDisk(harFolder+"/adjustData.har")

#%% [markdown]
# # END OF PROGRAM

