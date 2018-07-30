# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 14:53:23 2018
"""

import requests
import pandas as pd
import json
import ast
apiRoot = "http://pxnet2.stat.fi/PXWeb/api/v1/en/StatFin/"

def searchStatfin(phrase, base_url = apiRoot, language = "en"):
    """
    Search for data tables in StatFin API.
    base_url must be set to StatFin API root.
    Language can be one of the following: en, fi, sv 
    Search phrase specifies the query, and in must be a string.      
    The search is case INSENSITIVE.
    
    e.g.
    searchStatfin("employment")
    
    Several phrases can be used in a single search:
    searchStatfin("employment students")
    
    Output: dataframe with the location url for each match.
       
    """
    if language != "en":
        if language == "fi":
            base_url = "http://pxnet2.stat.fi/PXWeb/api/v1/fi/StatFin/"
        elif language == "sv":
            base_url = "http://pxnet2.stat.fi/PXWeb/api/v1/sv/StatFin/"
        else:
            raise ValueError("Language must be set either to 'en', 'fi' or 'sv'")
    if type(phrase) is not str:
        raise ValueError("Search phrase must be in string format!")
            
    convert = {'ä': 'a',   'ö': 'o',   'å': '%C3%A5', 'Å': '%C3%85',
               '"': '%22', '(': '%28', ')': '%29',    ' ': '%20'}
  
    search_str = '{base_url}/?query={phrase}'.format(
        base_url = base_url, 
        phrase = phrase)
    
    for k, v in convert.items():
        search_str = search_str.replace(k, v)
    
    df = pd.read_json(search_str)
    
    if len(df) == 0:
        print("No match")
        return df    

    df["path"] = df["path"].map(lambda x: x.strip("/"))
    
    df["urlDict"] = df["path"]+"/"+ df["id"]
    dfOut = df[["title", "urlDict", "published"]]
    
    return dfOut


def parseUrl(dataId, baseUrl=apiRoot):
    """
    Combine the StatFin API root address and data table ID to a functioning URL address.
    apiRoot is a http://... address
    dataId is a StatFin .px table location
    """
    fullUrl = baseUrl + dataId
    return fullUrl

def getParams(dataId, baseYear = None, filters = None, search = False):
    """
    Gets the available variables for the given data table.
    By default, this function gets all available variables for a given baseYear.
    However, since the accepted StatFin API query is limited to 110K entries, some
    data sets (particularly for capital time series) must be truncated
    by using filters.
    
    If baseYear is not specified, all available years are included in the query.
    Filter must be a dictionary, where the desired variable is the key, and
    the value is a list of filters. E.g: 
    
    filters = {"Sector": ["S1 Total economy", "S121 Central bank"],
               "Information": ["Current prices"]}
    
    The search-statement is by default set to False, but it can be used with 
    the filter option to return all options that contain the filter.
    E.g. filters = {"Sector": ["S13"]} only returns S13 General government when
    search = False. If search = True, it returns S13, S1311, S1313,...
    """
    
    # Some error checkings:
    if filters is not None:
        if type(filters) is not dict:
            raise ValueError("Filters must be in a dictionary! {'Filtered variable': [list of filters]}")
        if not all(type(value)==list for value in filters.values()):
            raise ValueError("All filter values must be stored inside a list! {'Filtered variable': [list of filters]}")
        
    fullUrl = parseUrl(dataId)
    allParams = pd.read_json(fullUrl)
    paramsList = [entry for entry in allParams.iloc[:,1]]
    varList = [var["code"] for var in paramsList]
    
    if filters is not None:
        if not set(filters.keys()).issubset(varList):
            errors = [e for e in filters.keys() if e not in varList]
            raise ValueError("FILTER(S) "+str(errors)+ " NOT AVAILABLE!")
    
    for x in paramsList:    
        if baseYear is not None:
            if x["code"] == "Vuosi":
                x["values"] = [str(baseYear)]
    
    if filters is not None:
        for i in filters:
            filterName = i
            filterVals = filters[i]

            if search:
                for z in paramsList:
                    if z["code"] == filterName:
                        z["values"] = [k for k in z["values"] if filterVals[0] in k]
                        if not z["values"]:
                            raise ValueError("Filter value "+filterVals[0]+" not found in StatFin data!")
            else:           
                for z in paramsList:
                    if z["code"] == filterName:
                        for val in filterVals:
                            if val not in z["values"]:
                                raise ValueError("Filter value "+val+" not included in the available parameters for "+ filterName)

                        z["values"] = filterVals
    return paramsList

def parseQuery(dataId, baseYear = None, filters = None, search = False):
    """Parses available parameters into a functioning API query."""
    params = getParams(dataId, baseYear, filters, search)
    nparams = len(params)
    params_list = list(range(nparams))
    query_element = {}
    
    for x in params_list:
        query_element[x] ='{{"code": "{code}", "selection": {{"filter": "item", "values": {values} }}}}'.format(                
                code = params[x]['code'],
                values = params[x]['values'])
        query_element[x] = query_element[x].replace("\'", '"')
    all_elements = str(list(query_element.values()))
    all_elements = all_elements.replace("\'", "")
    
    query = '{{"query": {all_elements} , "response": {{"format": "csv" }}}}'.format(all_elements = all_elements)
    
    # Flip the query back and forth from dictionary to json to get possible umlaut letters into API-compatible unicode:
    query = ast.literal_eval(query)
    query = json.dumps(query)
    
    return query


def getData(dataDict, baseYear = None, filters =None, search = False):
    """Perform the actual data query. Input must be a dictionary where keys are 
    (user-specifiable) names and values are StatFin table ids. Note that if 
    baseYear is not specified, all data is queried, which might cause API 
    requests to exceed their maximum size (110K data enries)."""
    for i in dataDict:
        
        dataId = dataDict[i]
        url = parseUrl(dataId)
        queryParams = parseQuery(dataId, baseYear, filters, search)
        r = requests.post(url, data= queryParams)
        # 403 Client Error
        if r.status_code == 403:
            dataLoc = None
            try: # Try to debug on the fly
                splitUrl = dataId.split("/")
                dataLoc = "http://pxnet2.stat.fi/PXWeb/pxweb/en/StatFin/StatFin__"+splitUrl[0]+"__"+splitUrl[1]+"/"+splitUrl[2]
            except:
                pass
            
            if dataLoc is not None:
                raise ValueError("Client error for "+str(i)+". Data query might be too large. Limit is 110K!\n Try a quick check at: "+dataLoc)
            else:
                raise ValueError("Client error for "+str(i)+". Data query might be too large. Limit is 110K!")

        # Everything ok:
        if r.status_code == 200:
            print(str(i)+" query OK")
        
        # Catch other possible status errors:
        r.raise_for_status()
            
        # Store the raw data in csv format into working directory:
        fileName = str(i)+"_Rawdata.csv"
        with open(str(fileName), 'wb') as output:
            output.write(r.content)