# alta

Python and GEMPACK code for constructing a CGE database for Finland using official published data.

### File list

* **CGE_basedata.ipynb**
Ipython notebook for creating the national core database (64 industries, 64 commodities)

* **dataGetterFunction**
Search and query the StatFin API database

* **checkerFunctions**
For quick data consistency checks

* **mapperFunction**
For mapping industries and commodities

* **harWriterFunction**
For writing pandas dataframes into header array (.har) format for GEMPACK
