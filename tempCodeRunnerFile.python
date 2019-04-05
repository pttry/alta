#%% [markdown]
# # Constructing a core CGE model database for Finland from published data
# 
# 
# This iPython notebook builds a core CGE model database for Finland using published national accounts data. First, raw data are queried from the Statistics Finland API, cleaned and filtered. Next, the initial data balance and model compatibility are tested. The steps for creating the actual database are explained in detail in the paper "Constructing a CGE Database Using GEMPACK for an African Country" by Roos, Adams and van Heerden. This notebook simply replicates those steps.
#%% [markdown]
# ### NATIONAL DATA (64 industries, 64 commodities)
# 
# 
# #### Import necessary Python modules:

#%%
# Basic Python packages (included in the Anaconda installation):

import pandas as pd # Python data analysis library: https://pandas.pydata.org/
import numpy  as np # Python scientific computing package: http://www.numpy.org/
import os           # Python operating system interface (for managing files and folders via this notebook)
import re           # Python regular expressions (Perl-style regular expression patterns). E.g. for matching string patterns.
import pickle       # To save intermediate data as objects

# HARPY module by Centre of Policy Studies. 
# Writes data from Python into Header Array (.har) format.
# Available at https://github.com/GEMPACKsoftware/HARPY or using directly through pip: pip install by harpy3
from harpy.har_file import HarFileObj
from harpy.header_array import HeaderArrayObj as HAO


# Other Python sequences in the working directory:
import dataGetterFunction as dgf  # To search and query the Statistics Finland API.
import harWriterFunction  as hwf  # A sequence that simplifies the output of large files.
import checkerFunctions as cfs    # Simple functions to quickly check data consistency by comparing column and row sums.
import mapperFunction as mf       # Function to map industries and commodities to an aggregate level.


#%%
# Choose base year for data:
baseYear = 2014
# Raw data folder:
rawFolder = "rawdata"
# Folder for output HAR-files:
harFolder = "hardata"
os.makedirs(harFolder, exist_ok=True)
# Location of bundle16 files from http://www.copsmodels.com/gpmark9.htm
bundle16Folder = "bundle16"

#%% [markdown]
# #### REMOVE OLD DATA?
# Set "remove" to eiher True or False. This removes old data versions from the current working directory, raw data directory and the output directory.

#%%
remove = False

flag = []
# Flags are used throughout this notebook just to stay on track
# what happens inside for-loops (or what doesn't happen).

redundants = ["csv", "log", "LOG", "gss", "gst", "bak", "har", "HAR", "inf", "min", "mnc"]
# All supplementary data is in .xlsx format, so don't remove those.

def remover(file, folder = None):
    if folder == None:
        filename = file
    else:
        filename = folder+"/"+file
    filetype = filename.split(".")[-1]
    if filetype in redundants:
        flag.append(filename)
        os.unlink(filename)
        print("Removed", filename)
    
if remove:
    for filename in os.listdir():
        remover(filename)
    for rawdata in os.listdir(rawFolder):
        remover(rawdata, rawFolder)
    for hardata in os.listdir(harFolder):
        remover(hardata, harFolder)

if not flag:
    print("Nothing was removed")

#%% [markdown]
# ## Specify data location in the StatFin API
# 
# Specify data location as a dictionary. The dictionary key is a (user-specified) name
# for the data, and the key must be the actual px-web location. If errors occur, use the dgf.searchStatfin("...") to check that the px-location is correct. Use, for instance, dgf.searchStatfin("supply table").

#%%
urlDict = {
"Supply table at basic prices":          "kan/pt/statfin_pt_pxt_001.px",
"Use table at basic prices":             "kan/pt/statfin_pt_pxt_002.px",
"Use table at purchasers prices":        "kan/pt/statfin_pt_pxt_003.px",
"Imports use table at basic prices":     "kan/pt/statfin_pt_pxt_005.px",
}


#%%
# Perform query. Raw data files (.csv) should appear in the rawdata directory.
# If baseYear is not specified, this will query data for all available years.

dgf.getData(urlDict, baseYear = baseYear)


#%%
# Read in raw data:
ioData = {k: pd.read_csv(rawFolder+"/"+str(k)+"_Rawdata.csv",encoding="utf-8",na_values =".") for k in urlDict.keys()} 

#%% [markdown]
# ## Clean the data
# 
# The function below renames all industries and commodities in raw data files by replacing the long names with the representative classification codes. It also adds different prefixes for industries ("I") and commodities ("C"). For example "01 Agriculture and hunting" is shortened to "I_01", and "10_12 Food products, beverages and tobacco" becomes "C_10_12". Also, to avoid later errors in GEMPACK, all instances of "/" are replaced with an underscore.
# 
# All industries and commodities are then collected to the lists IND and COM. They should be identical in size: 64 industries and 64 commodities. This might change in later data releases.

#%%
def splitNrename(df, attribute, prefix):
    """
    This function takes a DataFrame as input and cleans it from the long Statfin naming convention
    "number longname" to the model convention "PREFIX_number".
    E.g. "01 Agriculture and hunting" becomes "I_01" and "17 Paper and paper products" becomes "C_17".
    
    Inputs: DataFrame to be cleaned, attribute (column, index...) and a prefix ("C_" or "I_").
    """
    for x in getattr(df, attribute):
        dataCode = x.split(" ")[0]
        if "/" in dataCode:
            dataCode = dataCode.replace("/","_")
        if dataCode[0].isdigit():
            newName = prefix + dataCode
        else:
            newName = dataCode
        df.rename(**{attribute: {x:newName}}, inplace = True)    


#%%
# Clean the data:
for i in ioData:
    # Take only current prices data if also other available 
    if "Information" in ioData[i].columns:
        ioData[i] = ioData[i][ioData[i].Information == "Current prices"]
        ioData[i].drop("Information", axis = 1, inplace = True)
    # Replace missing values with zeros:
    ioData[i].fillna(0, inplace = True)
    # Set the product column as index:
    ioData[i].set_index("Product", inplace = True)
    # Drop redundant columns if they exist:
    for redundant in ["Year", "0 Industries total"]:
        if redundant in ioData[i].columns:
            ioData[i].drop(redundant, axis = 1, inplace = True)
    # Rename rows and columms using the splitNrename function above.
    # Note: commodities ("C_") are listed in the index and industries ("I_") are listed in columns.
    for attr, prefix in {"index": "C_", "columns": "I_"}.items():
        splitNrename(ioData[i], attr, prefix)


#%%
# Store available industries and commodities as lists:
IND = [ind for ind in ioData["Supply table at basic prices"].columns if ind[0:2] == "I_"]
COM = [com for com in ioData["Supply table at basic prices"].index if com[0:2] == "C_"]


#%%
# Check that the COM and IND dimensions are equal in length (original data is symmetrical):
print(len(IND) == len(COM))
print("Size is", len(IND), "x", len(COM))

#%% [markdown]
# #### Define different types of user groups and supply sources:

#%%
finUse = [   # Final users
"P51",       # Gross fixed capital formation
"P52",       # Changes in inventories
"P6K",       # Exports
"P3_S13",    # Government consumption
"P3_S14",    # Household consumption
"P3_S15"]    # Consumption by non-profit organisations

valAdd = [   # Value add components
"D1",        # Compensation of employees
"D29MD39",   # Other net taxes on production
"P51C",      # Consumption of fixed capital
"B13NT"]     # Operating surplus + mixed income 
    
supComp = [   # Supply components
"P7R_CIF",   # Imports at c.i.f. prices
"TRTP_MARG", # Trade and transport margins
"D21N"]      # Taxes less subsidies


#%%
# Filter out unwanted data entries and store results in a new dictionary called cleanData:
cleanData = {}
cleanData["usetable_PP"] = ioData["Use table at purchasers prices"].reindex(COM + valAdd)[IND + finUse]
cleanData["usetable_BP"] = ioData["Use table at basic prices"].reindex(COM + valAdd)[IND + finUse]
cleanData["supplytable_BP"]  = ioData["Supply table at basic prices"].reindex(COM)[IND+supComp]
cleanData["usetable_Imp_BP"] = ioData["Imports use table at basic prices"].reindex(COM + valAdd)[IND + finUse].fillna(0)

#%% [markdown]
# ### Check that the original raw data is balanced and consistent with the CGE model:
# 
# #### Check for negative values in original data
# 
# Negative values are only allowed in changes in inventories. Check that no negative values exist elsewhere in the original data. Possible negative values are set to zero and redistributed into changes in inventories (user code "P52"). Re-run this block to check that no negative values remain. Also check that if negative values exist, they are small.

#%%
flag = True
for commodity in COM:
    for user in IND + finUse:
        for priceType in ["PP", "BP"]: # Purchaser price, basic price
            if user != "P52": # Negative values are allowed in inventory changes, so exclude those
                dataLocation = cleanData["usetable_"+priceType].loc[commodity]
                if dataLocation[user] < 0:   
                    flag = False
                    negValue = dataLocation[user]                     
                    dataLocation["P52"] += negValue                   
                    dataLocation[user] = 0                           
                    print(priceType, user, commodity,": value", negValue, " assigned to changes in inventories!")
                    
if flag:
    print("OK! No negative values encountered.")

#%% [markdown]
# #### Check that current price GDP from income side equals GDP from expenditure side (well enough):

#%%
GDPexp = cleanData["usetable_PP"].loc[COM][finUse].sum().sum() - cleanData["supplytable_BP"]["P7R_CIF"].sum()
GDPinc = cleanData["usetable_PP"].loc[valAdd].sum().sum() + cleanData["supplytable_BP"].loc[COM]["D21N"].sum()

print("GDPexp is", GDPexp,"\nGDPinc is", GDPinc, "\nDifference is", GDPexp-GDPinc)

#%% [markdown]
# #### Check that aggregate supply (BP) equals aggregate demand (PP):

#%%
# Allow a small deviation:
allowDifference = 0.05


#%%
cfs.checkColSums(cleanData["supplytable_BP"].loc[COM], cleanData["usetable_PP"].loc[COM], allowDifference)

#%% [markdown]
# #### Check that national accounts identities hold in original data:
# 
# PP = BP - net taxes - margins from producer side + margins from user side
# 
# Basic flows = BP - margins = PP - taxes - margins
#%% [markdown]
# #### Check1: Purchaser's price - taxes = basic price (differences in margins)

#%%
# Margins inferred from data:
margtest=(cleanData["usetable_PP"].loc[COM] -          cleanData["usetable_BP"].loc[COM]).sum(axis=1)-cleanData["supplytable_BP"].loc[COM]["D21N"]
# Actual margins data
realmarg = cleanData["supplytable_BP"].loc[COM]["TRTP_MARG"]

cfs.checkCols(margtest, realmarg, allowDifference)

#%% [markdown]
# #### Check2: total sum of differences is near zero:

#%%
abs((margtest-realmarg).sum()) < allowDifference

#%% [markdown]
# #### Check3: domestic use equals domestic supply (MAKE_I)

#%%
# Check that supply and use by commodity is balanced:
domUse = cleanData["usetable_BP"].loc[COM].sum(axis=1) - cleanData["supplytable_BP"]["P7R_CIF"]
MAKE_I = cleanData["supplytable_BP"][IND].sum(axis=1)

cfs.checkCols(domUse, MAKE_I, allowDifference)

#%% [markdown]
# #### Check4: Basic price - basic flows - margins_C = 0, where 
# 
# basic flows =  PUR - tax - margins_M

#%%
# First, define total margins used per commodity
MAR_M = cleanData["supplytable_BP"].loc[COM]["TRTP_MARG"]
for i in MAR_M.index:
    if MAR_M.loc[i] < 0:
        MAR_M.loc[i] = 0      
# And total margins produced per margin commodity
MAR_C = cleanData["supplytable_BP"].loc[COM]["TRTP_MARG"]
for c in MAR_C.index:
    if MAR_C.loc[c] >= 0:
        MAR_C.loc[c] = 0
    else:
        MAR_C.loc[c] = MAR_C.loc[c] * (-1)


#%%
#Total flows:
flows_U = cleanData["usetable_PP"].loc[COM].sum(axis=1) - cleanData["supplytable_BP"].loc[COM]["D21N"] - MAR_M

# Check:
check4 = cleanData["usetable_BP"].loc[COM].sum(axis=1) - flows_U - MAR_C
cfs.checkCols(check4, pd.Series(0.0, index = COM), allowDifference)

#%% [markdown]
# #### Non-profit consumption P3_S15 is aggregated to household consumption P3_S14

#%%
for i in cleanData:
    if "P3_S15" in cleanData[i]:
        cleanData[i]["P3_S14"] += cleanData[i]["P3_S15"]
        cleanData[i].drop("P3_S15", axis = 1, inplace = True)

#%% [markdown]
# ## Factor payments
# 
# ### V1LAB (Labour compensation)
# 
# * From Use Table at purchaser's prices, select all industries and D1 (Compensation of employees). 
# * Split D1 using occupational shares from the public Mitenna database by The Ministry of Education (see /supplementaryData/Mitenna-info.txt)
# 

#%%
# Read in raw occupational data from MITENNA supplementary file:
OCC_levels = pd.read_excel("supplementaryData/MITENNA_"+str(baseYear)+".xlsx", skiprows = 1, index_col = 0)
OCC_levels.fillna(0, inplace=True)
# Drop redundant columns:
OCC_levels.drop(["Missing data", "Grand total"], axis = 1, inplace = True)
# Drop redundant rows:
OCC_levels.drop(["00000 Industry unknown", 
                 "Grand total",
                 "99000 Activities of extraterritorial organisations and bodies"], inplace = True)


#%%
# Clean up the index names and column names.
# For occupations: "02.3 Metal workers" becomes "O_02_3"
# For industries:  "01410 Raising of dairy cattle" becomes "I_01410, etc.

for occupation in OCC_levels:
    newName = "O_"+occupation.split(" ")[0].replace(".","_")
    OCC_levels.rename(columns = {occupation:newName}, inplace = True)
for industry in OCC_levels.index:
    # The Mitenna data might contain industry aggregates, such as "R Arts, entertainment and recreation", 
    # that do not directly match with the input-output industry numbering convention. The next step removes
    # all aggregate industry rows (those that start with a letter). Check that the total employment in 
    # these sectors is small enough to not cause any harm. 
    if re.search('[a-zA-Z]', industry[0]): 
        print("Dropped", industry,"with a total employment of", OCC_levels.loc[industry].sum(), "persons.")  
        OCC_levels.drop(industry, inplace = True)
             
    newName = "I_"+industry.split(" ")[0]
    OCC_levels.rename(index = {industry:newName}, inplace = True)


#%%
# Collect the +850 Mitenna industries to a single list:
mitennaIndustries = OCC_levels.index.tolist()
# And create a mapping from Mitenna to Statfin input-output industry classification:
mitennaIndMapper = mf.mapperFunction(mitennaIndustries, IND, exceptions={"I_68A":["I_68201", "I_68202"]})


#%%
# Aggregate the occupational data using the mappings specified above:
OCC_levels["MAPPING"] = pd.Series(mitennaIndMapper)
OCC_levels_agg = OCC_levels.groupby(["MAPPING"], sort = False).sum()

# Calculate industry specific occupation shares:
OCCshares = OCC_levels_agg.divide(OCC_levels_agg.sum(axis=1), axis = "index").fillna(0)

# Store the occupations dimension OCC to a list:
OCC = OCC_levels_agg.columns.tolist()

# And check that the number of workers in each occupation remains unchanged after aggregation:
cfs.checkCols(OCC_levels_agg.sum(), OCC_levels[OCC].sum(), allowDifference = 1)


#%%
# Split the original labour compensation data:
V1LAB_O = cleanData["usetable_BP"].loc["D1"][IND]
V1LAB   = OCCshares.multiply(V1LAB_O, axis = "index")

# Last, check that column sums still match the original data:
cfs.checkCols(V1LAB.sum(axis=1), V1LAB_O, allowDifference)

#%% [markdown]
# ### V1CAP (Capital rentals)
# V1CAP is the industry-specific gross operating surplus (GOS). It is calculated for each industry by summing the net operating surplus (B13NT) and capital depriciation (P51C).

#%%
V1CAP = cleanData["usetable_BP"].loc[["P51C", "B13NT"]].sum()
V1CAP = V1CAP[IND].to_frame("V1CAP")

# Negative V1CAP implies negative profits. The model doesn't allow for negative profits, 
# so check that all values for V1CAP are non-negative.
cfs.check4negs(V1CAP)

#%% [markdown]
# ### V1LND (Land rentals)
# 
# Next, the land rentals (V1LND) are separated for the land using sectors (agriculture, forestry, and mining) from V1CAP using the following shares:
# 
# * Agriculture: 15.0% $^{1}$ 
# * Forestry: 66% $^{2}$ 
# * Mining and quarrying: 7.7% $^{2}$ 
# 
# 
# 1. Land value / total farm assets. Source:  Statfin >> Agriculture, Forestry and Fishery >> Statistics on the finances of agricultural and forestry enterprises (35/41, Year 2014, Entire country)
# 
# 2. The share of land improvements / total assets. Source:  Statfin >> National Accounts >> Annual national accounts >> 017 -- Gross capital, Net capital, consumption and retirements of fixed capital 1975-2016 (N1123/TOT, Gross stock)

#%%
# Initialize V1LND as a zero vector:
V1LND = pd.DataFrame(0.0, index=IND, columns=["V1LND"])

# Specify lists of land-using industries:
agrInd = ["I_01"]          # Agriculture
forInd = ["I_02", "I_03"]  # Forest industry
minInd = ["I_05_09"]       # Mining
# Add construction industry?

V1LND.loc[agrInd] = V1CAP.loc[agrInd].multiply(0.150)
V1LND.loc[forInd] = V1CAP.loc[forInd].multiply(0.66)
V1LND.loc[minInd] = V1CAP.loc[minInd].multiply(0.077)

# Last, to avoid double counting, subtract V1LND from V1CAP
V1CAP["V1CAP"] -= V1LND["V1LND"]

#%% [markdown]
# ### Store user-specific purchaser's price values V1PUR-V6PUR

#%%
userNames = {
"V1": IND,          # Industry
"V2": ["P51"],      # Investment
"V3": ["P3_S14"],   # Households
"V4": ["P6K"],      # Export
"V5": ["P3_S13"],   # Government
"V6": ["P52"]}      # Inventories

# A single list containing all users:
userList = [item for sublist in userNames.values() for item in sublist]


#%%
VPUR_S = {} # Purchaser's price values summed over source dimension S (domestic/imported)
for i in userNames:
    VPUR_S[i+"PUR"] = cleanData["usetable_PP"].loc[COM][userNames[i]]
VPUR_US = cleanData["usetable_PP"].loc[COM].sum(axis=1) # VPUR summed over dimensions source S and user U

#%% [markdown]
# ### MAKE matrix (Multi-product matrix)

#%%
# Make matrix is simply extracted from the basic price supply table:
MAKE = cleanData["supplytable_BP"].loc[COM][IND].copy()

#%% [markdown]
# ### V1PTX (Production tax)

#%%
# From use table, read D29MD39 Other net taxes on production:
V1PTX = pd.DataFrame(cleanData["usetable_BP"].loc["D29MD39"][IND].copy())

#%% [markdown]
# ### V0TAR (Tariff revenue)
# 
# For import tariffs, only the total annual collected amount is available. It must be split between different commodities.

#%%
# Total tariff revenue is:
V0TAR_tot = 163.090 # m€
# Source: Finnish customs database at uljas.tulli.fi
# State revenue debited by Finnish Customs from 2001, indicator D.1.1. (customs duties)

# Total commodity specific imports are:
impByCom = cleanData["supplytable_BP"]["P7R_CIF"].copy()


# Tariff data is only collected from goods classified in the Combined Nomenclature (CN).
# Thus, set everything beyond C_32 to zero:
for commodity in COM:
    if int(commodity[2:4]) >= 33:
        impByCom[commodity] = 0
        
# Imports are at C.I.F prices, so we can calculate the tariff share as:
tariffShare = V0TAR_tot / impByCom.sum()

# Store the values to a DataFrame "V0TAR":
V0TAR = (impByCom * tariffShare).to_frame(name="V0TAR")

# Check that totals still match:
cfs.checkNums(V0TAR.sum(), V0TAR_tot, allowDifference = 0.05)

#%% [markdown]
# ### V1OCT (Other cost ticket)
# 
# For now, the other cost ticket is set to zero vector. In later stages, it can be used to handle e.g. pure profits and other miscellanious production costs.

#%%
V1OCT = pd.DataFrame(0.0, index = IND, columns = ["V1OCT"])

#%% [markdown]
# ### Import shares
# 
# Commodity-specific import shares are calculated as:
# 
# $IMPSHR(c) =   \frac{V0IMP(c)}{\sum{users} VPUR(c,u)}  $

#%%
# Total imports per commodity:
V0IMP = cleanData["supplytable_BP"].loc[COM]["P7R_CIF"]
# Commodity-specific import share:
IMP_SHR = (V0IMP/VPUR_US).fillna(0)
# Import share applied to all users:
importMatrix = cleanData["usetable_PP"].loc[COM].multiply(IMP_SHR, axis = "index")

#%% [markdown]
# ### Create margin matrices
# 

#%%
# Read margins data:
MARGIN = cleanData["supplytable_BP"]["TRTP_MARG"].copy()
# Margin commodities are those with negative values in national accounting:
MARGINCOMS = MARGIN[MARGIN<0]
MARGIN[MARGIN<0] = 0 

# Check that the total use and supply of margin commodities is in balance
MARGIN.sum() + MARGINCOMS.sum() < 0.01


#%%
# Store the margins dimension as a list:
MAR = MARGINCOMS.index.tolist()


#%%
# Inventories are excluded from margin use
marginUsers = [y for x in [v for k,v in userNames.items() if k != "V6"] for y in x]

#%% [markdown]
# The margin-use-ratios for each commodity are calculated as:
# 
# $MARUSERATIO(c) =   \frac{MARGIN(c)}{\sum{user}\sum{source} VPUR(u,s,c)}  $

#%%
MAR_USERATIO = (MARGIN / cleanData["usetable_PP"].loc[COM][marginUsers].sum(axis=1)).fillna(0)


#%%
# Next, calculate aggregate margin matrices for each user, summed over margin commodity M and source S:
MARGIN_DICT1 = {}
for i in VPUR_S:
    if "V6PUR" not in i:
        dataName = i
        keyName = i[0:2]+"MAR_S_M"
        MARGIN_DICT1[keyName] = VPUR_S[i].multiply(MAR_USERATIO, axis = "index")


#%%
# Check balance
marTotal1 = pd.DataFrame(0.0, index = COM, columns = ["TOTAL"])
for i in MARGIN_DICT1:
    if "V1" in i:
        marTotal1["TOTAL"] += MARGIN_DICT1[i].sum(axis = 1)
    else:
        marTotal1["TOTAL"] += MARGIN_DICT1[i].iloc[:,0]

cfs.checkCols(marTotal1["TOTAL"], MARGIN, allowDifference)

#%% [markdown]
# Next, the aggregate margins are split between different margin commodities:
# 
# $ MARSHR(m) = \frac{MARGIN(m)}{\sum MARGINS(m)}   $

#%%
MARGINS = pd.DataFrame(abs(MARGINCOMS))
MARGINS["MARSHR"] = MARGINS["TRTP_MARG"] / float(MARGINS.sum())


#%%
MARGIN_DICT2 = {}
for i in MARGIN_DICT1:
    dummyFrame  = pd.DataFrame(0.0, index = COM, columns = MARGINS.index)
    for j in MARGINS.index:       
        if "V1MAR" in i:
            keyName = i[0:-2]+"_"+j
            MARGIN_DICT2[keyName] = MARGIN_DICT1[i].multiply(MARGINS["MARSHR"].loc[j])
        else:
            dummyFrame[j] = MARGIN_DICT1[i] * MARGINS["MARSHR"].loc[j]
            MARGIN_DICT2[i[0:-2]] = dummyFrame


#%%
# CHECK THAT TOTAL MARGINS EQUAL THE VALUE FROM STATFIN DATABASE
marTotal2 = pd.DataFrame(0.0, index = COM, columns = ["TOTAL"])
for i in MARGIN_DICT2:
    if "V1" in i:
        marTotal2["TOTAL"] += MARGIN_DICT2[i].sum(axis = 1)
    else:
        marTotal2["TOTAL"] += MARGIN_DICT2[i].sum(axis = 1)
        
marTotal2["StatFin"] = MARGIN
cfs.checkCols(marTotal2["TOTAL"], marTotal2["StatFin"], allowDifference)


#%%
# Check that the margin use is correctly distributed between different margin commodities C45- C52
marComsDict = {}
for k in MARGINCOMS.index:
    marComsDict[k] = 0
    
for i in MARGINCOMS.index:
    for j in MARGIN_DICT2:
        if "V1MAR" in j:
            if i in j:
                marComsDict[i] += MARGIN_DICT2[j].sum().sum()
        else:
            marComsDict[i] += MARGIN_DICT2[j][i].sum()

errorList = []
for com in MARGINCOMS.index:
    diff = MARGINCOMS[com] + marComsDict[com]
    if abs(diff) > 0.001:
        print("ERROR IN", com, "BY", diff)
        errorList.append([com, diff])
if not errorList:
    print("No errors")


#%%
# Last, split the margins between domestic and imported sources.
MARGIN_DICT3 = {}
for i in MARGIN_DICT2:
    if "V4" not in i:
        user = i[0:2]
        multiplierImp = IMP_SHR
        multiplierDom = 1- multiplierImp
        newName = i.replace("_S","")

        impData = MARGIN_DICT2[i].multiply(multiplierImp, axis = "index")
        domData = MARGIN_DICT2[i].multiply(multiplierDom, axis = "index")

        MARGIN_DICT3[newName+"_imp"] = impData
        MARGIN_DICT3[newName+"_dom"] = domData
    else:
        newName = i.replace("_S","")
        MARGIN_DICT3[newName] = MARGIN_DICT2[i]


#%%
# Check margin totals: 
mar1chk =pd.Series(0.0, index =COM)
for k in MARGINCOMS.index:
    for s in ["_dom", "_imp"]:        
        mar1chk += MARGIN_DICT3["V1MAR_"+k+s].sum(axis=1)

mar2chk =MARGIN_DICT3["V2MAR_imp"].sum(axis=1)+MARGIN_DICT3["V2MAR_dom"].sum(axis=1)

mar3chk =MARGIN_DICT3["V3MAR_imp"].sum(axis=1)+MARGIN_DICT3["V3MAR_dom"].sum(axis=1)

mar4chk=MARGIN_DICT3["V4MAR"].sum(axis=1)

mar5chk =MARGIN_DICT3["V5MAR_imp"].sum(axis=1)+MARGIN_DICT3["V5MAR_dom"].sum(axis=1)

summa = sum([mar1chk,mar2chk,mar3chk,mar4chk,mar5chk])
cfs.checkCols(summa, MARGIN, allowDifference)


#%%
# These aggregate matrixes are used for quick balance checking later on:
V1MAR_C = pd.DataFrame(0.0, index = COM, columns = IND)
V2MAR_C = pd.DataFrame(0.0, index = COM, columns = ["MAR"])
V3MAR_C = pd.DataFrame(0.0, index = COM, columns = ["MAR"])
V4MAR_C = pd.DataFrame(0.0, index = COM, columns = ["MAR"])
V5MAR_C = pd.DataFrame(0.0, index = COM, columns = ["MAR"])

for i in MARGIN_DICT3:
    if "V1MAR" in i:
        data = MARGIN_DICT3[i].sum()     
        if "dom" in i:
            marCom = i[6:].replace("_dom", "")
        if "imp" in i:
            marCom = i[6:].replace("_imp", "")        
        V1MAR_C.loc[marCom] += data
  
    if "V2MAR" in i:    
        data = MARGIN_DICT3[i].sum() 
        marComs = MARGIN_DICT3[i].columns
        for k in marComs:
            V2MAR_C.loc[k] += data.loc[k]


    if "V3MAR" in i:    
        data = MARGIN_DICT3[i].sum() 
        marComs = MARGIN_DICT3[i].columns
        for k in marComs:
            V3MAR_C.loc[k] += data.loc[k]
            
    if "V4MAR" in i:    
        data = MARGIN_DICT3[i].sum() 
        marComs = MARGIN_DICT3[i].columns
        for k in marComs:
            V4MAR_C.loc[k] += data.loc[k]
            
    if "V5MAR" in i:    
        data = MARGIN_DICT3[i].sum() 
        marComs = MARGIN_DICT3[i].columns
        for k in marComs:
            V5MAR_C.loc[k] += data.loc[k]


#%%
# Check that margin use matches the supply of margin commodities:
cfs.checkNums(V1MAR_C.sum().sum() +V2MAR_C.sum() +V3MAR_C.sum() +V4MAR_C.sum() +V5MAR_C.sum(), abs(MARGINCOMS.sum()), allowDifference)


#%%
VMAR_M={}
for user in range(1,6):
    VMAR_M["V"+str(user)] = MARGIN_DICT1["V"+str(user)+"MAR_S_M"]

#%% [markdown]
# ### Indirect tax matrices

#%%
TAXBYCOM  = pd.DataFrame(cleanData["supplytable_BP"]["D21N"].copy())

# Following Roos et al. (2015), it is supposed that households pay most of the tax burden.
# A tax weight factor is therefore assigned, giving households a weight factor of 3, and all other
# users a weight factor of 1

#TAXFAC = pd.DataFrame(1.0, index = userList, columns = ["TAXFAC"]).sort_index()
#TAXFAC.loc["P3_S14"] = 3.0

TAXFAC = pd.DataFrame(1.0, index = userList, columns = ["TAXFAC"])
TAXFAC = pd.DataFrame(ioData["Use table at basic prices"][TAXFAC.index.values].loc["D21N"]/ioData["Use table at basic prices"][TAXFAC.index.values].loc["FIMUSE_OH"], columns=["TAXFAC"]).fillna(0)


WTOT =   cleanData["usetable_PP"].loc[COM].T.multiply(TAXFAC["TAXFAC"], axis="index").sum()


#%%
taxMatrix = pd.DataFrame(0.0, index = COM, columns = userList)
for i in taxMatrix.index:
    taxMatrix.loc[i] = TAXFAC["TAXFAC"]


#%%
TAX = taxMatrix.multiply(TAXBYCOM["D21N"], axis = "index")
VTAX=(cleanData["usetable_PP"].loc[COM][userList]*TAX).divide(WTOT, axis = "index").fillna(0)


#%%
taxDict = {}
taxDict["V1TAX_S"] = VTAX[IND]
taxDict["V2TAX_S"] = VTAX["P51"]
taxDict["V3TAX_S"] = VTAX["P3_S14"]
taxDict["V4TAX_S"] = VTAX["P6K"]
taxDict["V5TAX_S"] = VTAX["P3_S13"]
taxDict["V6TAX_S"] = VTAX["P52"]


#%%
# Check totals:
taxTotal = pd.DataFrame(0.0, index = COM, columns = ["TOTAL"])
for user in taxDict:
    if user == "V1TAX_S":
        taxTotal["TOTAL"] += taxDict[user].sum(axis=1)
    else:
        taxTotal["TOTAL"] += taxDict[user]
cfs.checkCols(TAXBYCOM, taxTotal, allowDifference)


#%%
# Split taxes between domestic and imported:
taxDict2 = {}
for user in taxDict:
    for source in ["dom", "imp"]:
        keyName = user[0:5]+source
        origData = taxDict[user]
        if source == "dom":
            newData = origData.multiply(1-IMP_SHR, axis = "index")
        else:
            newData = origData.multiply(IMP_SHR, axis = "index")
        taxDict2[keyName] = newData

#%% [markdown]
# ### Create matrices for basic flows
# 
# Note: The model basic flows (V*BAS) are NOT the same as Statistics Finland basic price (BP) values. Importantly, the commodity-specific margin use must be deducted from the BP values to get the corresponding BAS entry:
# 
# $BAS_{(u,c,dom)} = \sum_{s \in SRC}VPUR_{(u,c,s)} - BAS_{(u,c,imp)} - \sum_{s \in SRC} \sum_{m \in MAR} MAR_{(u,c,s,m)} -  \sum_{s \in SRC} TAX_{(u,c,s)} $

#%%
V1BASimp = importMatrix[IND]
V2BASimp = importMatrix["P51"]
V3BASimp = importMatrix["P3_S14"]
V4BASimp = importMatrix["P6K"]
V5BASimp = importMatrix["P3_S13"]
V6BASimp = importMatrix["P52"]


#%%
V1BASdom = cleanData["usetable_PP"].loc[COM][IND]      - V1BASimp - VMAR_M["V1"] - taxDict["V1TAX_S"]
V2BASdom = cleanData["usetable_PP"].loc[COM]["P51"]    - V2BASimp - VMAR_M["V2"].iloc[:,0] - taxDict["V2TAX_S"]
V3BASdom = cleanData["usetable_PP"].loc[COM]["P3_S14"] - V3BASimp - VMAR_M["V3"].iloc[:,0] - taxDict["V3TAX_S"]
V4BAS    = cleanData["usetable_PP"].loc[COM]["P6K"]    - V4BASimp - VMAR_M["V4"].iloc[:,0] - taxDict["V4TAX_S"]
V5BASdom = cleanData["usetable_PP"].loc[COM]["P3_S13"] - V5BASimp - VMAR_M["V5"].iloc[:,0] - taxDict["V5TAX_S"]
V6BASdom = cleanData["usetable_PP"].loc[COM]["P52"]    - V6BASimp - taxDict["V6TAX_S"]


#%%
# Basic flows for V3-V6 have only two dimensions (commodity and source) so they can be compiled to single dataframes:
V3BAS = pd.DataFrame(0, index=COM, columns=["DOM", "IMP"])
V4BAS = V4BAS.to_frame(name = "V4BAS")
V5BAS = pd.DataFrame(0, index=COM, columns=["DOM", "IMP"])
V6BAS = pd.DataFrame(0, index=COM, columns=["DOM", "IMP"])

V3BAS["DOM"] = V3BASdom
V3BAS["IMP"] = V3BASimp

V5BAS["DOM"] = V5BASdom
V5BAS["IMP"] = V5BASimp

V6BAS["DOM"] = V6BASdom
V6BAS["IMP"] = V6BASimp


#%%
# Check that no negative values or nan values have emerged:
for i in [V1BASdom, pd.DataFrame(V2BASdom), V3BAS, V4BAS, V5BAS]:
    cfs.check4negs(i)
    cfs.check4nans(i)

#%% [markdown]
# ### Split investments between industries
#%% [markdown]
# Next, industry dimension is added to V2PUR.
# Industry-specific capital rental share is used as a starting point:
# 
# IND_SHR(i) = $\frac{V1CAP(i)}{\sum V1CAP(i)} $

#%%
IND_SHR = V1CAP/V1CAP.sum()

# Initialize an empty matrix in IND * COM dimension
indShareMatrix = pd.DataFrame(0.0, index = COM, columns = IND)

# Copy industry share to each row
for i in IND:
    indShareMatrix[i] = float(IND_SHR.T[i]) #

#%% [markdown]
# Next, more detail is added by employing capital formation data from the national accounts, where industry-specific investments are available for different asset groups. The commodity coverage of these assets is limited, but capturing the shares in main investment groups such as buildings and machinery is already a major improvement. In 2014, for instance, buildings and structures accounted for over 55 % of all investments. Machinery and transport equipment accounted for another 20 %.

#%%
# Query the data on gross fixed capital formation:
urlDict = {"Gross fixed capital": "kan/vtp/statfin_vtp_pxt_016.px"}
dgf.getData(urlDict, baseYear = baseYear, filters= {"Tiedot": ["CP"]})


#%%
# Read in data:
capData = {k: pd.read_csv(rawFolder+"/"+str(k)+"_Rawdata.csv",encoding="utf-8",na_values =".") for k in urlDict.keys()} 
invData = capData["Gross fixed capital"].fillna(0)


#%%
# Clean data:
for col in invData:
    if col in ["Industry", "Sector", "Transaction", "Asset", "Type"]:
        invData[col] = invData[col].apply(lambda x: x.split(" ")[0]) 
    if col == "Industry":
        invData[col] = invData[col].apply(lambda k: "{}{}".format("I_", k))
invData.drop("Information", axis =1, inplace = True)

# ToDo: why are these not automatically in numeric form?
invData[str(baseYear)] =invData[str(baseYear)].apply(pd.to_numeric, errors='coerce')


#%%
# Industry names in StatFin input-output data and national accounts do not directly match

# Conversion of industry names from national accounts data to IO data.
# Please check that these are up-to-date.
differences = {
"I_B": "I_05_09",   # Mining and quarrying 
"I_F": "I_41_43",   # Construction
"I_I": "I_55_56",   # Accommodation and food service activities
"I_O": "I_84",      # Public administration and social security
"I_681+68209+683": "I_68",  # Real estate activities
"I_68201_68202":   "I_68A"} # Operation of dwellings


#%%
# Rename the old names using the dictionary specified above:
invData.replace(differences, inplace = True)
# Quick check that all elements of IND are found in the capital accounts data:
for i in IND:
    if i not in invData.Industry.unique():
        raise ValueError("Industry", i, "not found in data!")
# And keep only the data for industries in IND and for sectors in "S1 Total economy".
invData2 = invData[(invData["Industry"].isin(IND)) & (invData["Sector"] == "S1")].reset_index(drop = True).copy()


#%%
# Investment assets and commodities are matched as follows:
comAssets = {
"Construction": ["C_41_43"],           # N111+N112 Buildings and structures --> Construction
"Transport": ["C_29", "C_30"],         # N1131 Transport equipment --> Motor vehicles, Other transport equipment
"Machinery": ["C_26", "C_27", "C_28"], # N1132+N1139 ICT equip. and other machinery --> 
                                       # Computer and electronic products, electrical equipment,
                                       # Other machinery and equipment
"Intellectual": ["C_71", "C_72"],      # N117 Intellectual property rights --> Architectural and engineering services; 
}                                      # technical testing and analysis services, 
                                       # Scientific research and development services


#%%
# For the investment assets specified above, filter the industry-specific investment levels.
# The reindexing is juts to make sure that the ordering of industries is maintained.
invLevels = {}
invLevels["Construction"] = invData2[invData2["Asset"] == "N111+N112"].set_index("Industry")[str(baseYear)].reindex(IND)
invLevels["Transport"]    = invData2[invData2["Asset"] == "N1131"].set_index("Industry")[str(baseYear)].reindex(IND)
invLevels["Machinery"]    = invData2[invData2["Asset"] == "N1132+N1139"].set_index("Industry")[str(baseYear)].reindex(IND)
invLevels["Intellectual"] = invData2[invData2["Asset"] == "N117"].set_index("Industry")[str(baseYear)].reindex(IND)


#%%
# Set negative investment values to zero if they exist.
# Also, turn the investment levels into industry-specific shares.
invShares = {}
flag = True
for asset in invLevels:
    for i in invLevels[asset].index:
        if invLevels[asset].loc[i] < 0:
            flag = False
            value = invLevels[asset].loc[i]
            invLevels[asset].loc[i] = 0
            print(asset, i, "set from", value, "to zero!")
    invShares[asset] = invLevels[asset] / invLevels[asset].sum()
if flag:
    print("Ok! No negative values found!")


#%%
# Modify the original industry share matrix:
for asset in comAssets:
    for com in comAssets[asset]:
        indShareMatrix.loc[com] = invShares[asset]


#%%
# Last, split data using the new shares:
V2BASdom = indShareMatrix.multiply(V2BASdom, axis = "index")
V2BASimp = indShareMatrix.multiply(V2BASimp, axis = "index")

taxDict2["V2TAXdom"] = indShareMatrix.multiply(taxDict2["V2TAXdom"], axis ="index")
taxDict2["V2TAXimp"] = indShareMatrix.multiply(taxDict2["V2TAXimp"], axis ="index")

VPUR_S["V2PUR"] = indShareMatrix.multiply(VPUR_S["V2PUR"]["P51"], axis = "index")

for k in MARGINCOMS.index:
    for s in ["dom", "imp"]:
        MARGIN_DICT3["V2MAR_"+k+"_"+s] = indShareMatrix.multiply(MARGIN_DICT3["V2MAR_"+s][k], axis = "index")


#%%
# Drop redundant aggregates
for key in ['V2MAR_imp', 'V2MAR_dom']:
    try:
        del MARGIN_DICT3[key]
    except:
        print(key, "not found in data. No changes made.")

#%% [markdown]
# # Check balance

#%%
# DIFFIND is COSTS-MAKE_C : should be near zero
allowDifference = 0.005
DIFFIND = pd.DataFrame(0.0, index = IND, columns = ["COSTS", "MAKE_C", "DIFFERENCE"])

#Value ad
DIFFIND["COSTS"] += V1LAB_O
DIFFIND["COSTS"] += V1CAP["V1CAP"]
DIFFIND["COSTS"] += V1LND["V1LND"]
DIFFIND["COSTS"] += V1PTX["D29MD39"]
DIFFIND["COSTS"] += V1OCT["V1OCT"]

DIFFIND["COSTS"] += V1BASdom.sum()
DIFFIND["COSTS"] += importMatrix[IND].sum()
DIFFIND["COSTS"] += taxDict["V1TAX_S"].sum()
DIFFIND["COSTS"] += VMAR_M["V1"].sum()

DIFFIND["MAKE_C"] += MAKE.sum()

DIFFIND["DIFFERENCE"] = DIFFIND["COSTS"] - DIFFIND["MAKE_C"]
difData1 = DIFFIND[abs(DIFFIND["DIFFERENCE"]) > allowDifference]


#%%
# If there is a difference, transfer it into V1CAP
for ind in difData1.index:
    value = difData1.loc[ind]["DIFFERENCE"]
    if abs(value) > 1:
        raise ValueError("Assertion does not hold! Difference too big!")
    print("For", ind, "V1CAP is adjusted by", value)
    V1CAP.loc[ind] -= value
if difData1.empty:
    print("No errors, no adjustments made")

# Check that after the adjustment all entries in V1CAP remain non-negative
cfs.check4negs(V1CAP)


#%%
difData1


#%%
MARGSALES = pd.DataFrame(0.0, index = COM, columns = ["MARGSALES"])
for i in MARGINCOMS.index:
    MARGSALES["MARGSALES"][i] = abs(MARGINCOMS[i])

# DIFFCOM is COM_OUTPUT - COM_USE : should be zero
DIFFCOM = pd.DataFrame(0.0, index = COM, columns = ["OUTPUT", "USE", "DIFFERENCE"])

DIFFCOM["OUTPUT"] += MAKE.sum(axis=1)

DIFFCOM["USE"] += V1BASdom.sum(axis = 1)
DIFFCOM["USE"] += V2BASdom.sum(axis = 1)
DIFFCOM["USE"] += V3BASdom
DIFFCOM["USE"] += V4BAS["V4BAS"]
DIFFCOM["USE"] += V5BASdom
DIFFCOM["USE"] += V6BASdom
DIFFCOM["USE"] += MARGSALES["MARGSALES"]

DIFFCOM["DIFFERENCE"] = DIFFCOM["OUTPUT"] - DIFFCOM["USE"]

difData2 = DIFFCOM[abs(DIFFCOM["DIFFERENCE"]) > allowDifference]


#%%
for com in difData2.index:
    value = difData2.loc[com]["DIFFERENCE"]
    if abs(value) > 1:
        raise ValueError("Assertion does not hold! Difference too big!")
    print("For", com, "V6BAS is adjusted by", value)
    V6BASdom.loc[com] +=  value
if difData2.empty:
    print("No errors, no adjustments made")

#%% [markdown]
# ### Some parameters and coefficients for model homogenity testing

#%%
paramSheets =[sheet for sheet in pd.read_excel("supplementaryData/PARAMETERS64.xlsx", sheet_name=None)]


#%%
paramDict = {}
for sheet in paramSheets:
    paramDict[sheet] = pd.read_excel("supplementaryData/PARAMETERS64.xlsx", sheet_name = sheet)


#%%
paramNames = {
"1ARM": "Intermediate Armington",
"2ARM": "Investment Armington",
"3ARM": "Households Armington",
"ITEX": "Flag, >0.5 for individual export coms, else collective export",
"LCOM": "Flag for regional extension, >0.5 for local coms, else national",
"LIND": "Local industries",
"P018": "Traditional Export Elasticities",
"P028": "Primary Factor Sigma",
"SCET": "Output Sigma",
"SLAB": "Labour Sigma",
"XPEL": "Household Expenditure Elasticities"}


#%%
# Store data as numpy arrays before exporting them as HAR files
V1BAS = np.stack((V1BASdom.values, V1BASimp.values), axis=1)
V2BAS = np.stack((V2BASdom.values, V2BASimp.values), axis=1)

V1TAX = np.stack((taxDict2["V1TAXdom"].values, taxDict2["V1TAXimp"].values), axis = 1)
V2TAX = np.stack((taxDict2["V2TAXdom"].values, taxDict2["V2TAXimp"].values), axis = 1)
V3TAX = pd.concat([taxDict2["V3TAXdom"],taxDict2["V3TAXimp"]], axis = 1)
V4TAX = taxDict["V4TAX_S"]
V5TAX = np.stack((taxDict2["V5TAXdom"].values, taxDict2["V5TAXimp"].values), axis = 1)
V6TAX = np.stack((taxDict2["V6TAXdom"].values, taxDict2["V6TAXimp"].values), axis = 1)


#%%
#note dstack = along the 3rd dimension for margins!
V1MAR = np.stack([
np.dstack([MARGIN_DICT3[key].values for key in MARGIN_DICT3.keys() if "V1MAR" in key and "dom" in key]),\
np.dstack([MARGIN_DICT3[key].values for key in MARGIN_DICT3.keys() if "V1MAR" in key and "imp" in key])], axis=1)

V2MAR = np.stack([
np.dstack([MARGIN_DICT3[key].values for key in MARGIN_DICT3.keys() if "V2MAR" in key and "dom" in key]),\
np.dstack([MARGIN_DICT3[key].values for key in MARGIN_DICT3.keys() if "V2MAR" in key and "imp" in key])], axis=1)

V3MAR = np.stack((MARGIN_DICT3["V3MAR_dom"].values, MARGIN_DICT3["V3MAR_imp"].values), axis = 1)
V4MAR = MARGIN_DICT3["V4MAR"]
V5MAR = np.stack((MARGIN_DICT3["V5MAR_dom"].values, MARGIN_DICT3["V5MAR_imp"].values), axis = 1)


#%%
allDims = {
"COM": COM,            # Commodities
"IND": IND,            # Industries
"OCC": OCC,            # Occupations
"SRC": ["DOM", "IMP"], # Sources
"MAR": MAR}            # Margins


#%%
baseData={
#coefficient name: (dataset, header name, long name, [list of dimensions])
"V1CAP": (V1CAP, "1CAP", "Capital rentals", ["IND"]),
"V1LND": (V1LND, "1LND", "Land rentals", ["IND"]),
"V1LAB": (V1LAB, "1LAB", "Labor compensation", ["IND", "OCC"]),
"MAKE":  (MAKE,  "MAKE", "Multi-production matrix", ["COM", "IND"]),
"V1PTX": (V1PTX, "1PTX", "Production tax", ["IND"]),
"V0TAR": (V0TAR, "0TAR", "Tariff revenue", ["COM"]),
"V1OCT": (V1OCT, "1OCT", "Other cost ticket", ["IND"]),
# Basic flows    
"V1BAS": (V1BAS, "1BAS", "Intermediate basic", ["COM", "SRC", "IND"]),
"V2BAS": (V2BAS, "2BAS", "Investment basic", ["COM", "SRC", "IND"]),
"V3BAS": (V3BAS, "3BAS", "Household basic", ["COM", "SRC"]),
"V4BAS": (V4BAS, "4BAS", "Export basic", ["COM"]),
"V4BASimp": (V4BASimp, "4BAi", "Export basic", ["COM"]),   
"V5BAS": (V5BAS, "5BAS", "Government basic", ["COM", "SRC"]),
"V6BAS": (V6BAS, "6BAS", "Inventories basic", ["COM", "SRC"]),
# Basic taxes    
"V1TAX": (V1TAX, "1TAX", "Intermediate tax", ["COM", "SRC", "IND"]),
"V2TAX": (V2TAX, "2TAX", "Investment tax", ["COM", "SRC", "IND"]),
"V3TAX": (V3TAX, "3TAX", "Household tax", ["COM", "SRC"]),
"V4TAX": (V4TAX, "4TAX", "Export tax", ["COM"]),
"V5TAX": (V5TAX, "5TAX", "Government tax", ["COM", "SRC"]),
"V6TAX": (V6TAX, "6TAX", "Inventories tax", ["COM", "SRC"]),
# Margins
"V1MAR": (V1MAR, "1MAR", "Intermediate margins", ["COM", "SRC", "IND", "MAR"]),
"V2MAR": (V2MAR, "2MAR", "Investment margins", ["COM", "SRC", "IND", "MAR"]),
"V3MAR": (V3MAR, "3MAR", "Household margins", ["COM", "SRC", "MAR"]),
"V4MAR": (V4MAR, "4MAR", "Export margins", ["COM", "MAR"]),
"V5MAR": (V5MAR, "5MAR", "Government margins", ["COM", "SRC", "MAR"]),
# Parameters
"SIGMA1": (paramDict["1ARM"], "1ARM", "Intermediate Armington", ["COM"]),
"SIGMA2": (paramDict["2ARM"], "2ARM", "Investment Armington", ["COM"]),
"SIGMA3": (paramDict["3ARM"], "3ARM", "Household Armington", ["COM"]),
"IsIndivExp": (paramDict["ITEX"], "ITEX", "Flag for individual export commodities", ["COM"]),    
"IsLocCom":   (paramDict["LCOM"], "LCOM", "Flag for regional extension > 0.5 for local coms, els national", ["COM"]),
"EXP_ELAST":  (paramDict["P018"], "P018", "Individual export elasticities", ["COM"]),
"SIGMA1PRIM": (paramDict["P028"], "P028", "Primary factor sigma", ["IND"]),
"SIGMA1OUT":  (paramDict["SCET"], "SCET", "Output sigma", ["IND"]),
"SIGMA1LAB":  (paramDict["SLAB"], "SLAB", "Labour sigma", ["IND"]),
"EPS": (paramDict["XPEL"], "XPEL", "Household expenditure elasticities", ["COM"]),
# Constants
"EXP_ELAST_NT": (2.0, "EXNT", "Collective export elasticity", []),
"FRISCH": (1.5, "P021", "Frisch parameter", []),
"BASEYEAR": (baseYear, "BYER", "Data base year", [],),
"ALPHA1": (0.4, "ALF1", "Wage adaptation coefficient", []),
"ALPHA2": (0.0, "ALF2", "Employment adaptation coefficient", []),
}


#%%
# Write the dimensions as sets. Also include the regional data:
output = {**allDims, **baseData}


#%%
hwf.data2har(output, allDims).writeToDisk(harFolder+"/basedata64.har")

#%% [markdown]
# # Creating AGGSUP.har supplementary file for aggregating data
#%% [markdown]
# #### Data used for weighted aggregations

#%%
V1PRIM = V1LAB_O + V1CAP["V1CAP"] + V1LND["V1LND"]
V1MAT = VPUR_S["V1PUR"].sum()
V1CST = V1PRIM + V1OCT["V1OCT"] + V1MAT
V1TOT = V1CST + V1PTX["D29MD39"]
V2TOT = VPUR_S["V2PUR"].sum()


#%%
V1PUR_SI = VPUR_S["V1PUR"].sum(axis=1)
V2PUR_SI = VPUR_S["V2PUR"].sum(axis=1)
V3PUR_S  = VPUR_S["V3PUR"]["P3_S14"]
V4PUR    = VPUR_S["V4PUR"]["P6K"]

#%% [markdown]
# #### Mappings for direct aggregation
# 
# Commodities and Industries are mapped to match the level at which regional data is available.

#%%
# Query for regional industy classification: (StatFin: Output and employment by region)
regIndRaw = [x["values"] for x in dgf.getParams("kan/altp/statfin_altp_pxt_008.px", "names") if x["code"] == "Toimiala"][0]
# ['0', '01', '02_03', '05_09', '10_12', '13_15', '16', '17_18', '19_22', '23', '24_25', '26_27', 
# '28', '29_30', '31_33', '35_39', '41_43', '45_47', '49_53', '55_56', '58_63', '64_66', '681+68209+683', 
# '68201_68202', '69_75', '77_82', '84', '85', '86_88', '90_96', '97_98']


#%%
renameInd = {           # From regional accounts naming convention to input-output convention
"681+68209+683": "68",  # Other real estate activities  --> Real estate activities
"68201_68202"  : "68A"} # Letting and operation of dwellings  --> Operation of dwellings and residential real estate

regInd = [renameInd.get(n, n) for n in regIndRaw if n != "0"] # Rename and drop "0" (Industries total)

# Last, add the prefix "I_" to all regional industries:
regInd = ["I_"+i for i in regInd]
# And prefix "C_" for commodities:
regCom = ["C_" + c[2:] for c in regInd]


#%%
# Mapping from IND to regInd and COM to regCom
MIND = mf.mapperFunction(IND, regInd)
MCOM = mf.mapperFunction(COM, regCom)


#%%
aggSup={
#coefficient name: (dataset, header name, long name, [list of dimensions])
"V1TOT":  (V1TOT,    "1TOT", "Industry output", ["IND"]),
"V2TOT":  (V2TOT,    "2TOT", "Investment by industry", ["IND"]),
"V1PRIM": (V1PRIM,   "VLAD", "Total factor input to industry", ["IND"]),
"V1LAB_O":(V1LAB_O,  "1LAB", "Industry wages", ["IND"]),
"V1PUR":  (V1PUR_SI, "1PUR", "Intermediate use at purch. price", ["COM"]),
"V2PUR":  (V2PUR_SI, "2PUR", "Investment use at purch. price", ["COM"]),
"V3PUR":  (V3PUR_S,  "3PUR", "Consumption at purch. price", ["COM"]),
"V4PUR":  (V4PUR,    "4PUR", "Export at purch. price", ["COM"])}


#%%
WAGG = [
# Headers that are used in weighted aggregations for elasticities and ratios
"1ARM 1PUR",
"2ARM 2PUR",
"3ARM 3PUR",
"XPEL 3PUR",
"P018 4PUR",
"P028 VLAD",
"SLAB 1LAB",
"SCET 1TOT"
]


#%%
aggDims = {
"COM": COM,     # All commodities 
"IND": IND,     # All industries
"ACOM": regCom,  # Regional commodities
"AIND": regInd,  # Regional industries
"WAGG": WAGG,    # Headers for weighted aggregation
"MCOM": [str(c) for c in MCOM.values()],
"MIND": [str(i) for i in MIND.values()]
}

aggSupData = {**aggDims, **aggSup}
aggSupHar = hwf.data2har(aggSupData, aggDims)

# Mappings are created to MCOM and MIND.
# Mappings must be specified using long_name. Note! 70 characters.

aggSupHar.getHeaderArrayObj("MCOM").__setitem__("long_name", "Mapping MCOM from COM(64) to ACOM(30)                                 ")
aggSupHar.getHeaderArrayObj("MIND").__setitem__("long_name", "Mapping MIND from IND(64) to AIND(30)                                 ")


#%%
aggSupHar.writeToDisk(harFolder+"/AGGSUP.har")

#%% [markdown]
# # Save clean/basedata

#%%
inter_folder = "interdata"
os.makedirs(inter_folder, exist_ok=True)
pickle.dump(cleanData, open(inter_folder+"/cleanData.p", "wb"))

table_dims = {"COM": COM, 
              "IND": IND,
              "finUse": finUse,
              "valAdd": valAdd,
              "supComp": supComp}

pickle.dump(table_dims, open(inter_folder+"/table_dims.p", "wb"))

#%% [markdown]
# # END OF PROGRAM

