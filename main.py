""" 
Main file to create regional input-ouput-tables

See README/dataprocess.txt for details


"""
import harWriterFunction  as hwf
import os
from shutil import copyfile


import importlib
importlib.reload(hwf)

# 1. Create national base data
# ############################

# Run CGE.basedata.ipynb (IPython notebook) step-by-step.
# - Output: basedata64.har, AGGSUP.har


# 3. Data for regional extension (top-down regional split)
# ########################################################
# Run CGE_regional_extension.ipynb notebook step-by-step.
# - intermediate output: basedata30.har
# - Output: regExtension.har, REGSUPP.har
# Previous step 2 included


# 4. Merge the aggregated basedata and regional extensions
# ########################################################
# Run mergehars.bat
# - Output: basedata.har

hwf.mergeHAR("hardata", "basedata30.har", "regExtension.har", "basedata.har")



# 5. Test the merged data for homogenity
# ######################################
# copy the new basedata.har into the oranig2013 folder for test.
copyfile("hardata/basedata.har", "oranig2013/basedata.har")
# Run oranig2013/homogtest.bat




# This step uses the ORANI-G (2013 version) that is available from the
# Centre of Policy Studies website (copsmodels.com archive, TPMH0110).
# Here, the numeraire variable (exchange rate phi) is given a shock of +10%.
# For a homogenous dataset, this should produce a +10% change in all
# endogenous variables.

# Before running the test, make sure that a fresh version of the basedata
# has been copied (basedata.har) to the oranig2013 folder.

# Results are written to htest.sl4.

# (VATT_mallien_data_seloste kohta 4.)



# 6. Capital data for model dynamics
# ##################################
# Run CGE_capital_dynamics.ipynb step-by-step
# - Output: capital.har, capitalextra.har, adjustdata.har

# (VATT_mallien_data_seloste kohta 5.)



# 7. Update the old basedata using inputs from capital accounts
# #############################################################
# Run basedataupdate.bat
# Output: basedataNEW.har

# In the capital data, the depreciation rates and rates of return are capped
# to 20% and recalculated. The difference is allocated to V1OCT (other cost ticket)
# to maintain data balance. Thesee new entries are added to the old data in this .bat file.

# The .bat file also copies the new files into TERM folder, where they are later needed.

# Tästä todennäköisesti puuttuu jotain: muutoksia saattaa tulla myös V1LABiin (jos toiminta-
# ylijäämiä siirretään) sekä kaikkiin V2-alkuisiin virtoihin.

# (VATT_mallien_data_seloste kohta 5. (adjustdata.tab))


# 8. Create data for government accounts
# ######################################
# Run CGE_data_base_government_accounts.ipynb
# -Output: govdata.har, govextra.har, govsecsplit.har

# (VATT_mallien_data_seloste kohta 6.)



# 9. Sum public sector data over different sectors
# ################################################
# Run govgeneric.bat
# -Output: govacc.har, govextra2.har, base-extra.har

# (VATT_mallien_data_seloste kohta 6. govgeneric.tab Tämän pitäisi myös tarkastaa
# aineiston tasapaino, mutta tablo-ohjelma on sen suhteen keskeneräinen).




# 10. Regional split of input-output data (TERM)
# #############################################
# The actual dirty work of creating regional data.
# In the TERM/data folder, refer to the regdata.doc for detailed instructions (by Mark Horridge).
# mkdata.bat runs the data manipulation sequence.
# Remember to copy files national.har and regsupp.har to the TERM/data folder before starting.

# Note: due to the errors in linear RAS procedure, the original mkdata.bat is modified to include 
# only the traditional RAS procedure. The number of steps is set to 1000. Also the
# aggregation procedures have been switched off.
# - Output: premod.har, orgsets.har, aggsuppVERM.har

# (VATT_mallien_data_seloste kohta 10.)


# 11. Combine extra-files into a single har
# #########################################
# Run extramerge.bat
# -Output: natextra.hra

# Again, using mergehar auxiliary program.



# 12. Regional split for capital
# ###############################
# Run regcapital.bat
# -Output: regrorext.har, v1check.har, regextra.har, regextra_lag.har, regsets.har

# Capital data is divided to different regions simply by using shares from V1CAP, that was
# split in step 10.
# Most important stuff in regextra.har

