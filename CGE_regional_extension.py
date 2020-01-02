#%% [markdown]
# # Regional extension
# 
# ORANI-G model uses a top-down regional split, and requires regional shares as input.
# 
# This notebook compiles estimates for:
# 
# * Regional output shares (REGSHR1, R001)
# * Regional investment shares (REGSHR2, R002)
# * Regional consumption shares (REGSHR3, R003)
# * Regional export shares (REGSHR4, R004)
# * Regional government spending shares (REGSHR5, R005)
# * Regional inventory shares (REGSHR6, R006)

#%%
# Basic modules
import pandas as pd
import numpy  as np

# HARPY module by Centre of Policy Studies for writing data into Header Array (HAR) format.
# Available at https://github.com/GEMPACKsoftware/HARPY
from harpy.har_file import HarFileObj
from harpy.header_array import HeaderArrayObj as HAO

import dataGetterFunction as dgf
import harWriterFunction as hwf
import checkerFunctions as cfs


#%%
# Choose base year for data:
baseYear = 2014
# Raw data folder:
rawFolder = "rawdata"
# Folder for output HAR-files:
harFolder = "hardata"


#%%
### Aggregation


#%%
hwf.aggHAR(harFolder, "basedata64.har", "basedata30.har", "AGGSUP.har")


#%%
# Define regional data location:
urlDict = {
"Output and employment by region":    "kan/altp/statfinpas_altp_pxt_008_201600.px",
"Households' transactions by region": "kan/altp/statfinpas_altp_pxt_016_201600.px"}

# Get data:
dgf.getData(urlDict, baseYear = baseYear, active=False)


#%%
# Check the available regions from regional accounts:
print([x["valueTexts"] for x in dgf.getParams("kan/altp/statfinpas_altp_pxt_008_201600.px", "kunnat") if x["code"] == "Alue"][0])


#%%
# Choose regions and rename if necessary:
REGIONS ={
"Uusimaa":        "Uusimaa", 
"Varsinais-Suomi":"VarsinSuomi", 
"Satakunta":      "Satakunta", 
"Kanta-Häme":     "KantaHame", 
"Pirkanmaa":      "Pirkanmaa", 
"Päijät-Häme":    "PaijatHame",    
"Kymenlaakso":    "Kymenlaakso", 
"South Karelia":  "EtelaKarjala", 
"Etelä-Savo":     "EtelaSavo", 
"Pohjois-Savo":   "PohjSavo", 
"North Karelia":  "PohjKarjala", 
"Central Finland":"KeskiSuomi", 
"South Ostrobothnia":  "EtelaPohjanm",
"Ostrobothnia":        "Pohjanmaa", 
"Central Ostrobothnia":"KeskiPohjanm", 
"North Ostrobothnia":  "PohjPohjanm",
"Kainuu":  "Kainuu", 
"Lapland": "Lappi", 
"Åland":   "Ahvenanmaa"}

REG = [r for r in REGIONS.values()]


#%%
# Read in regional data:
regionalData = {k: pd.read_csv(rawFolder+"/"+str(k)+"_Rawdata.csv",
                               # Use different encoding to display umlaut letters correctly:
                               encoding="ISO-8859-1", 
                               na_values =".") for k in urlDict.keys()}


#%%
# Clean and rename:
for k in regionalData:
    regionalData[k].fillna(0, inplace = True)
    regionalData[k] = regionalData[k][regionalData[k]["Area"].isin(list(REGIONS.keys()))]
    
    for col in regionalData[k]:
        if col in ["Industry", "Sector", "Transaction"]:
            # Get the code, drop the long name:
            regionalData[k][col] = regionalData[k][col].apply(lambda x: x.split(" ")[0]) 
        
        if col == "Industry":
            # Add the prefix "I_" for all industries:
            regionalData[k][col] = regionalData[k][col].apply(lambda x: "{}{}".format("I_", x))
            # Drop redundant aggregates:
            regionalData[k].drop(regionalData[k][regionalData[k].Industry.isin(["I_0"])].index, inplace=True)
    # Rename:                    
    regionalData[k].replace({**REGIONS, 
                             **{"Current prices":"CP", "At previous year`s prices": "FP"},
                             **{"I_681+68209+683": "I_68", "I_68201_68202": "I_68A"}}, inplace = True)
            
    regionalData[k].reset_index(drop = True, inplace= True)   


#%%
regOutput = regionalData["Output and employment by region"].copy()
regHH = regionalData["Households' transactions by region"].copy()


#%%
regBaseData = HarFileObj.loadFromDisk(harFolder+"/basedata30.har")

regInd = regBaseData.getHeaderArrayObj("IND")["array"].tolist()
regCom = regBaseData.getHeaderArrayObj("COM")["array"].tolist()
regSrc = regBaseData.getHeaderArrayObj("SRC")["array"].tolist()
regMar = regBaseData.getHeaderArrayObj("MAR")["array"].tolist()

regInd = [i.strip(' ') for i in regInd]
regCom = [c.strip(' ') for c in regCom]
regSrc = [s.strip(' ') for s in regSrc]
regMar = [m.strip(' ') for m in regMar]


#%%
# Check that industries in the aggregated basedata match with the regional data:
set(regOutput.Industry) == set(regInd)

#%% [markdown]
# ### Regional shares are derived from following data:
# 
# * **R001 Regional output:** StatFin --> National accounts --> Regional account --> Output and employment, 30 industries --> P1R Output at basic prices
# * **R002 Regional investment:** StatFin --> National accounts --> Regional account --> Output and employment, 30 industries --> P51TOT Gross fixed capital formation
# * **R003 Regional consumption:** StatFin --> National accounts --> Regional account --> Households' transactions --> B6NT Disposable income, net
# * **R004 Regional export:** Customs --> International trade in goods by region
# * **R005 Regional government:** StatFin --> National accounts --> Regional account --> Households' transactions --> KVAKI Mean population
# * **R006 Regional inventories:** = Set according to R002

#%%
# First, collect levels data for all required entries:
regLevels = {}


#%%
# REGOUTPUT contains:

# P1R     Output at basic prices
# P2K     Intermediate consumption
# B1GPHT  Value added, gross at basic prices
# D1K     Compensation of employees
# E1_1H   Employment, persons
# E11_1H  Employment, self-employed (persons)
# E12_1H  Employees, persons
# E2_T    Total hours worked (1,000 hours)
# E21_T   Hours worked, self-employed (1,000 hours)
# E22_T   Hours worked, employees (1,000 hours)
# P51TOT  Gross fixed capital formation

regInfos = {      # Dimensions:
"R001": "P1R",    # (IND, REG)
"R002": "P51TOT"} # (IND, REG)


#%%
for i in regInfos:
    data = regOutput[(regOutput["Transaction"] == regInfos[i]) & (regOutput["Sector"] == "S1") & (regOutput["Data"] == "CP")]
    pivotData = data.pivot(index = "Industry", columns = "Area", values = str(baseYear))
    regLevels[i] = pivotData


#%%
# REGHH contains:

# B2NT:   Operating surplus, net
# B3NT:   Mixed income, net
# D11R_2: Wages and salaries (incl. employee stock options)
# D12R:   Employers' social contributions
# D4R_2:  Property income (including holding gains and losses)
# D4K:    Property expenditure
# B5NT1:  National income / balance of primary incomes, net
# D62R:   Social benefits other than social transfers in kind, receivable
# D7R:    Other current transfers, receivable
# D5K:    Current taxes on income and wealth, etc., payable
# D61K:   Social contributions, payable
# D7K:    Other current transfers, payable
# B6NT:   Disposable income, net
# KVAKI:  Mean population (persons)

regInfos2 = {      # Dimensions:
"R003": "B6NT",    # (COM, REG)
"R005": "KVAKI"}   # (COM, REG)

# Initialize empty dataframes:
for num in ["R003", "R004", "R005"]:
    regLevels[num] = pd.DataFrame(0.0, columns=REG, index = regCom)


#%%
for j in regInfos2:
    print(regInfos2[j])
    data = regHH[regHH["Transaction"] == regInfos2[j]].set_index("Area")[str(baseYear)]
    print(data)
    for r in REG:
        regLevels[j][r] = data.loc[r]

print("ok2")

#%%
# Inventory shares are set equal to the investment shares. 
# However, the index is IND for investment, and COM for inventories, so swap them accordingly:
regLevels["R006"] = regLevels["R002"].rename(index= dict(zip(regInd, regCom)))


#%%
gg=pd.read_csv("supplementaryData/Export_regional.csv", sep=';', encoding="ISO-8859-1")


#%%
g=gg.set_index('mk')


#%%
regExports ={k:g.loc[k][str(baseYear)] for k in REG}


#%%
# Export data from customs: (m€)
regExports2 ={
"Uusimaa":      19522, 
"VarsinSuomi":  3806, 
"Satakunta":    3852, 
"KantaHame":    1471, 
"Pirkanmaa":    4125, 
"PaijatHame":   1655,    
"Kymenlaakso":  4886, 
"EtelaKarjala": 1309, 
"EtelaSavo":    399, 
"PohjSavo":     1093, 
"PohjKarjala":  804, 
"KeskiSuomi":   1904, 
"EtelaPohjanm": 594,
"Pohjanmaa":    3266, 
"KeskiPohjanm": 1616, 
"PohjPohjanm":  1572,
"Kainuu":       144, 
"Lappi":        3291, 
"Ahvenanmaa":   85}

for r in regExports:
    regLevels["R004"][r] = regExports[r]


#%%
# Sort dataframes:
for frame in regLevels:
    regLevels[frame] = regLevels[frame][REG]    


#%%
# Check that negative values don't exist.
# If they do, the next step will set them to zero. Then, re-run this block, and the next.
for x in regLevels:
    print(x)
    cfs.check4negs(regLevels[x])


#%%
# Set negative values for zero. Check that the values are small!!
flag = True
for x in regLevels:
    for i in regLevels[x].index:
        for c in regLevels[x].columns:
            value = regLevels[x].loc[i][c]
            if value < 0:
                flag = False
                regLevels[x].loc[i][c] = 0
                print(x,i,c, "was set to zero!")
if flag:
    print("Ok! No negative values found")


#%%
# Convert from levels to shares:
regShares = {}
for data in regLevels:
    levelsData = regLevels[data]
    rowSum = levelsData.sum(axis = 1)
    sharesData = levelsData.div(rowSum, axis = 0)
    regShares[data] = sharesData
    # If the sumRow has entries with 0, it will cause division by zero and NAN values.
    # If that occurs, replace them with a uniform value 1 / number of regions
    for ix in rowSum.index:
        if rowSum.loc[ix] == 0:
            regShares[data].loc[ix] = 1/len(REG)


#%%
# Check that NAN values don't exist:
for x in regShares:
    print(x)
    cfs.check4nans(regShares[x])

#%% [markdown]
# ### Other regional support data

#%%
# Regional dimensions:
allDims = {
"COM": regCom,
"IND": regInd,
"SRC": regSrc,
"REG": REG,
"MAR": regMar,
}


#%%
# Regional population:
regPop = regHH[regHH["Transaction"] == "KVAKI"].set_index("Area")
PO01 = regPop[str(baseYear)].to_frame(name = "RPOP")

# Shortest distance from r to d:
DIST = pd.read_excel("supplementaryData/regDistances.xlsx", index_col = 0)

# Distance factor for gravity formula
DFAC = pd.DataFrame(1.0, index = regCom, columns = ["dom", "imp"])
DFAC.loc[["C_35_39", "C_41_43","C_68", "C_68A"]] = 2.0

# Margin weighting
MWGT = pd.DataFrame(1.0, index = REG, columns =allDims["MAR"])

# Distance related margins
DMAR = ["C_49_53"]

# Tendency to be locally sourced
LMAR = pd.DataFrame(1.0, index = allDims["MAR"], columns = ["LOCMAR"])
LMAR.loc["C_45_47"] = 3.0

# Between-region Armington
SGDD = pd.DataFrame(5.0, index = regCom, columns = ["SIGMADOMOM"])

# Elasticity of substitution between regions of margin product
SMAR = pd.DataFrame(0.2, index = allDims["MAR"], columns = ["SIGMAMAR"])

# Truly local commodities
RLOC = ["C_68", "C_68A", "C_85", "C_86_88"]

# Share of national imports, by port of entry
MSHR = pd.DataFrame(1/len(REGIONS), index = regCom, columns = REG)


#%%
# Regional employment:
regEmp = regOutput[(regOutput["Transaction"] == "E1_1H") &
                   (regOutput["Sector"] == "S1") &
                   (regOutput["Data"] == "CP")].groupby(["Area"]).sum().reindex(REG)

#%%

# Regional share of labour compenstation
labCompensation = regionalData["Output and employment by region"][(regionalData["Output and employment by region"]["Transaction"] == "D1K") &                                                 (regionalData["Output and employment by region"]["Sector"] == "S1") &                                                 (regionalData["Output and employment by region"]["Data"] == "CP")]

labCompensation = labCompensation.drop(["Sector", "Data", "Transaction"], axis = 1)
labCompensation = labCompensation.pivot(index = "Industry", columns = "Area", values = str(baseYear))
labCompensation = labCompensation[REG]

cfs.check4negs(labCompensation)

rowsum = labCompensation.sum(axis=1)
labCompenShares = labCompensation.divide(rowsum, axis = "index")

#%% [markdown]
# ### Output data to HAR format

#%%
regData={
#coefficient name: (dataset, header name, long name, [list of dimensions])

# Regional extension data
"REGSHR1": (regShares["R001"], "R001", "Regional output shares", ["IND", "REG"]),
"REGSHR2": (regShares["R002"], "R002", "Regional investment shares", ["IND", "REG"]),
"REGSHR3": (regShares["R003"], "R003", "Regional consumption shares", ["COM", "REG"]),
"REGSHR4": (regShares["R004"], "R004", "Regional export shares", ["COM", "REG"]),
"REGSHR5": (regShares["R005"], "R005", "Regional government shares", ["COM", "REG"]),
"REGSHR6": (regShares["R006"], "R006", "Regional inventory shares", ["COM", "REG"]),
"REGSHR7": (labCompenShares, "R007", "Regional labour compensation shares", ["IND", "REG"]),
}


#%%
regSupp = {   
"RPOP":      (PO01, "PO01", "Regional population",["REG"]),    
"DISTANCE":  (DIST, "DIST", "Shortest distance",  ["REG", "REG"]),
"DISTFAC":   (DFAC, "DFAC", "Distance factor",    ["COM", "SRC"]),    
"MWGT":      (MWGT, "MWGT", "Margin weighting",   ["REG", "MAR"]), 
"DMAR":      DMAR,   # Set
"LMAR":      (LMAR, "LMAR", "Tendency to be locally sourced", ["MAR"]),    
"SIGMADOMOM":(SGDD, "SGDD", "Between-region Armington", ["COM"]),    
"SIGMAMAR":  (SMAR, "SMAR", "Elasticity of substitution between regions of margin production",["MAR"]),
"RLOC":      RLOC,  # Set
"REGIMPSHR": (MSHR, "MSHR", "Regional import share", ["COM", "REG"]),
"EMPLOY_R":  (regEmp, "EMPR", "Employment by region", ["REG"]),
}


#%%
# Write the dimensions as sets. Also include the regional data:
output = {**allDims, **regData}
hwf.data2har(output, allDims).writeToDisk(harFolder+"/regExtension.har")


#%%
output = {**allDims, **regSupp}
hwf.data2har(output, allDims).writeToDisk(harFolder+"/REGSUPP.har")

#%% [markdown]
# ## Output data to nympy
#%% [markdown]
# # END OF PROGRAM

