""" 
Main file to create regional input-ouput-tables

See README/dataprocess.txt for details


"""
import harWriterFunction  as hwf
import os
from shutil import copyfile


# import importlib
# importlib.reload(hwf)

# 1. Create national base data
# ############################

# Run CGE.basedata.ipynb (IPython notebook) step-by-step.
# - Output: basedata64.har, AGGSUP.har

exec(open('CGE_basedata.py', encoding = "UTF-8").read())


# 3. Data for regional extension (top-down regional split)
# ########################################################
# Run CGE_regional_extension.ipynb notebook step-by-step.
# - intermediate output: basedata30.har
# - Output: regExtension.har, REGSUPP.har
# Previous step 2 included

exec(open('CGE_regional_extension.py', encoding = "UTF-8").read())

# 4. Merge the aggregated basedata and regional extensions
# ########################################################
hwf.mergeHAR("hardata", "basedata30.har", "regExtension.har", "basedata.har")
# - Output: basedata.har


# 5. Test the merged data for homogenity
# ######################################
# copy the new basedata.har into the oranig2013 folder for test.
copyfile("hardata/basedata.har", "oranig2013/basedata.har")
# Run oranig2013/homogtest.bat

# This step uses the ORANI-G (2013 version) that is available from the
# Centre of Policy Studies website (copsmodels.com archive, TPMH0110).
# Results are written to htest.sl4.

# 6. Capital data for model dynamics
# ##################################
# Run CGE_capital_dynamics.ipynb step-by-step
# - Output: capital.har, capitalextra.har, adjustdata.har


# 7. Update the old basedata using inputs from capital accounts
# #############################################################
hwf.mergeHAR("hardata", "basedata.har", "adjustData.har", "basedataNEW.har")
# Output: basedataNEW.har

# copy the new files into TERM folder, where they are later needed.
copyfile("hardata/basedataNEW.har", "TERM/national.har")
copyfile("hardata/REGSUPP.har", "TERM/REGSUPP.har")


# 8. Create data for government accounts
# ######################################
# Run CGE_data_base_government_accounts.ipynb
# -Output: govdata.har, govextra.har, govsecsplit.har

# (VATT_mallien_data_seloste kohta 6.)


# 9. Sum public sector data over different sectors
# ################################################
hwf.govgeneric()
# -Output: govacc.har, govextra2.har, base-extra.har



# 10. Regional split of input-output data (TERM)
# #############################################
hwf.mkdata2()
# - Output: premod.har, orgsets.har, aggsuppVERM.har
copyfile("TERM/premod.har", "hardata/premod.har")
copyfile("TERM/orgsets.har", "hardata/orgsets.har")



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

