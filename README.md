# alta

Python and GEMPACK code for constructing a CGE database for Finland using official published data.

### Yleistä:

* TODO-lista: katso dataprocess.txt

### File list

* **CGE_basedata.ipynb**
Ipython notebook for creating the national core database (64 industries, 64 commodities)

* **CGE_regional_extension.ipynb**
Regional extension to the core module.

* **dataGetterFunction.py**
Search and query the StatFin API database.

* **checkerFunctions.py**
For quick data consistency checks.

* **mapperFunction.py**
For mapping industries and commodities.

* **harWriterFunction.py**
For writing pandas dataframes into header array (.har) format for GEMPACK.

* **mergaHars.bat**
Procedure for combining .har files.

* **regionalAggregation.bat**
.bat command sequence for aggregating .har data.

* **oranig2013 folder**
ORANI-G model, used for model homogenity testing.

* **TERM folder**
TERM model, used for regional split of data.


# Data process: 


### 1. Create national base data

Run CGE.basedata.ipynb (IPython notebook) step-by-step.
- Output: basedata64.har, AGGSUP.har

This step works with non-aggregated StatFin input-output data, with
64 industries and commodities.
  
Note: the Statfin regional accounts only has data for some 30 industries. 
The file AGGSUP.har is used to aggregate the national data (basedata.har) to the regional 
level.At the time of writing, the harpy Python routine does not allow for directly
specifying mappings in the IPython notebook. Therefore, the mapping from
IND64 to IND30 and COM64 to COM30 must be specified manually in ViewHar.

An example AGGSUP.har containing mappings is stored in the supplemenaryData folder.




### 2.Aggregate national data to regional level (IND and COM dimensions)

This step uses the aggsup.har file created earlier in Step 1.
Remember, the mapping needs to be specified manually inside HAR file
(that is, mappings MIND (from IND64 to IND30) and MCOM (from COM64 to COM30).
The aggregation is performed using the GEMPACK auxiliary program called
Agghar. This can be done with the command sequence regionalAggregation.bat
(or see agghar guide from GEMPACK website).
- Output: basedata30.har




### 3. Data for regional extension

Run CGE_regional_extension.ipynb notebook step-by-step.
This creates regional shares for output, investment, consumption etc.
Also other regional data, from population to distances, are specified here.
- Output: regExtension.har, REGSUPP.har



### 4. Merge the aggregated basedata and regional extensions

This combines the aggregated base data and the regional supplementary data 
.har files into one HAR called national.har.



### 5. Test the merged data for homogenity (ORANI-G)

This step uses the ORANI-G (2013 version) that is available from the
Centre of Policy Studies website (copsmodels.com archive, TPMH0110).
Here, the numeraire variable (exchange rate phi) is given a shock of +10%.
For a homogenous dataset, this should produce a +10% change in all
endogenous variables.

Copy national.har to the folder oranig2013 and run the program
oranig.tab using htest.cmf command file (tets.bat does this).
Results are written to htest.sl4.


### 6. Regional split (TERM)

The actual dirty work of creating regional data.
In the TERM/data folder, refer to the regdata.doc for detailed instructions (by Mark Horridge).
mkdata.bat runs the data manipulation sequence.
Remember to copy files national.har and regsupp.har to the TERM/data folder before starting.

Note: due to the errors in linear RAS procedure, the original mkdata.bat is modified to include 
only the traditional RAS procedure. The number of steps is set to 1000. Also the
aggregation procedures have been switched off.
- Output: premod.har, orgsets.har

