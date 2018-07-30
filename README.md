# alta

Python and GEMPACK code for constructing a CGE database for Finland using official published data.

### Yleistä:
* Tapaaminen Tilastokeskuksella torstaina 16.8 klo 10, jolloin saadaan käyttöön tarkempi aineisto marginaaleista, veroista sekä tuonnin osuuksista.

### File list

* **CGE_basedata.ipynb**
Ipython notebook for creating the national core database (64 industries, 64 commodities)

* **CGE_regional.ipynb**
Regional extension to the core module. Coming soon.

* **dataGetterFunction.py**
Search and query the StatFin API database

* **checkerFunctions.py**
For quick data consistency checks

* **mapperFunction.py**
For mapping industries and commodities

* **harWriterFunction.py**
For writing pandas dataframes into header array (.har) format for GEMPACK

### Database creation process (WORK IN PROGRESS!)
1. Run CGE_basedata.ipynb. This creates the core national database and a supplementary file for regional extension. Specify elasticities and other necessary parameters in the supplementaryData folder.
2. Regional accounts are only availeble for 30 industries, so national data must be aggregated before proceeding. This is done using the GEMPACK auxiliary program AGGHAR (regionalAggregation.bat).
3. Regional extension
4. Homogenity testing
5. Add COFOG data
6. Add capital data for model dynamics
7. Add balance of payments data
