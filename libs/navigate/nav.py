# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 13:06:29 2021

@author: 
    Krishnaprasd Sobhen(ksobhen)
    Tapasya Maji(tmaji)
    Yoshinori Ushiyama(yushiyam)
@version: 3.0

This module manages the route api's and route annotation datsets for the map 

@functions:
    -getLatLon - finds lat,lon for a given location name using openStreetmap module(nominatim) of geocoder and verifies that it is in USA
    -planRoute - uses Map box or Open Source Routing Machine(fall back) api to get fastest route from origin to destination
    -backupRouteObj - saves route object for future examination
    -getRouteObj - loads the saved route object
    
    -addUSA - add usa to location name if not supplied by user to avoid ambigity for nominatim
    -checkIfUSA - verify that the returned location is infact in usa
    -loadMapData - load map json file for us states and counties based on file name supplied
    -getStates - from geometry data of states and routeobject(array of lat,lon) detremine states through which route passes through
    -getCounties - from geometry data of counties, a list of states and the routeobject(array of lat,lon) detremine counties through which route passes through
    -getLineRoute - returns route object((lat,lon) array) as a lineString(shapely object)
    -minDistToRoute - returns the shortest distance in miles between a given point and a route line

    -getGeoDf - convert given data from to geoPandas dataframe with a column containing geo data as the input
    -getRouteAnnotations - find crime and pandemic risk annotation info for received route object 


@version history:
    -v1- get lat lon for a given location name
    -v2- verification of location name and lat lon for US territories
    -v3- get route for a given pair of origin and destination
    -v4- get list of states a given route passes through
    -v5- identify minimum distance to route for a given point
    -v6- get list of counties a given route passes through 
    -v7- get annotations output for a given route and risk data 
"""
import sys,os
sys.path.append(os.path.dirname(__file__))
path=os.path.dirname(__file__)+"./data/"

import osrm_nav as osrm
import mapbox_nav as mapbox

import geopandas
from geopy.geocoders import Nominatim
from geopy import distance
import numpy as np
import json
from shapely.geometry import shape, Point,LineString
from shapely.ops import nearest_points



def getLatLon(location):
    pt={}
    status="success"
    geolocator = Nominatim(user_agent="EVantage") # use OSM Nominatim service to get lat,lon for a location name
    try:
        # verifies if input and output are definitly in USA
        location=addUSA(location) 
        pt=geolocator.geocode(location).raw
        if(checkIfUSA(pt["display_name"])==False):
            status="Give a location in USA!"
    except:
        # error message if no matches are found
        pt={'lon':None,'lat':None}
        status="Cant find given address,try making the input more specific"
    finally:
        return ((pt['lon'],pt['lat']),status) # returns a status message and lat,lon coordinates if successful
    
def planRoute(start_point,stop_point,newKey=True):
    try:
        if(newKey): # loads a key and searches for a given route - can hot swap keys
            routrObj=mapbox.getRouteObject(start_point,stop_point,mapbox.getKey().strip()) # hits mapbox api for driving -much more reliable and fast
        else:
            routrObj=mapbox.getRouteObject(start_point,stop_point) 
    except:# hits osrm api for driving -if key fails in mapbox
        start_point_nr=osrm.getNearest(start_point)
        stop_point_nr=osrm.getNearest(stop_point)
        routrObj=osrm.getRouteObject(start_point_nr,stop_point_nr,"full") # load data with full route map
    return routrObj
        
def backupRouteObj(routeObj,start_point,stop_point):
    with open(path+'routes/saveRoute'+start_point+'_'+stop_point+'.txt', 'w') as file:
          file.write(json.dumps(routeObj))
         
def getRouteObj(fileName):
    with open(path+'routes/'+fileName, 'r') as file:
        return json.load(file)

def addUSA(location):
    test=location.lower().strip()
    if any(s in test for s in [',united states', ',us']):
        return test
    elif(test[-1]==','):
        return test+'usa'
    else:
        return test+',usa'
    
def checkIfUSA(name):
    if(name.split(",")[-1].strip()=='United States'):
        return True
    return False

def loadMapData(fname='USStateBounds.txt'):
    with open(path+fname) as f: # https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_040_00_500k.json
        data = json.load(f)
    return data

def getStates(ptList,stateData):
    states=[]
    route=getLineRoute(ptList)
    for index,feature in enumerate(stateData['features']): # parse through state geometry
        polygon = shape(feature['geometry']) # convert lat,lon to polygons
        if(polygon.intersects(route)|polygon.contains(route)): # if given route intersects a state or lies within it addd name to states list
            states.append(feature['properties']['NAME'])
    return list(set(states)) # make the state list unique

def getCounties(ptList,countiesData,statList):
    extractStates=[]
    counties=[]
    route=getLineRoute(ptList)
    for county in countiesData: # similar logic as getStates except it filters for counties in given state list for faster operation
        if(county['fields']['state_name'] in statList):
            extractStates.append({
                "state":county['fields']['state_name'],
                "county":county['fields']['name'],
                "geo":county['fields']['geo_shape']})                                                                                
    for county in extractStates:
        polygon = shape(county["geo"])
        if(polygon.intersects(route)|polygon.contains(route)):
            counties.append({"county":county['county'],"state":county['state']})
    return counties
    

def getLineRoute(inputRoute):
    return LineString(inputRoute) # converts route to line string

def minDistToRoute(pt,route):
    closest_point = nearest_points(route, pt)[0] # find nearest route point  to given point
    distance_miles = distance.distance((closest_point.y,closest_point.x), (pt.y,pt.x)).miles # calculate distance in miles between the two points
    return distance_miles

def getGeoDf(df,colName='poly'):
    data_geo=geopandas.GeoDataFrame(df, geometry=colName) # converts given input to geo dataframe
    return data_geo
    
def getRouteAnnotations(routeLocations,countiesDispData):#get annotations output for a given route and risk data 
    riskIndex=[]
    crimeRiskIndex=[]
     # for faster computation use a step size of 20 when parsing route object else the same size route object -very short route
    stepSize=20 if routeLocations.shape[0]>20 else routeLocations.shape[0]
    # iterate route at 20 steps
    for index1 in range(0,routeLocations.shape[0],stepSize):
        row=routeLocations.iloc[index1]
        pt=Point(row['lon'],row['lat']) # convert to shapely point object
        pandemicRiskVal=[] # stores risk index
        crimeRiskVal=[]
        for index2,county in countiesDispData[countiesDispData.disp_risk_index.notnull()].iterrows():
            if(county['poly'].contains(pt)): # check if given point is present in a county
                pandemicRiskVal=county['disp_risk_index'],# if so assign associated riskindex as first elemt of array
                crimeRiskVal=county['disp_crime_index']
                break # exit loop  once found and look for next point
        riskIndex=np.append(riskIndex,np.repeat(pandemicRiskVal,stepSize)) # replicate first element of riskIndex 20 times to extrapolate values
        crimeRiskIndex=np.append(crimeRiskIndex,np.repeat(crimeRiskVal,stepSize))
    # if the final array size doesnt fit the route size - trim or extrapolate within a range of 20 steps to match distance
    if(routeLocations.shape[0]>len(riskIndex)):
        riskIndex=np.append(riskIndex,np.repeat(riskIndex[-1],(routeLocations.shape[0]-len(riskIndex))))
        crimeRiskIndex=np.append(crimeRiskIndex,np.repeat(crimeRiskIndex[-1],(routeLocations.shape[0]-len(crimeRiskIndex))))
    elif(routeLocations.shape[0]<len(riskIndex)):
         riskIndex=riskIndex[0:routeLocations.shape[0]]
         crimeRiskIndex=crimeRiskIndex[0:routeLocations.shape[0]]
    return riskIndex,crimeRiskIndex # return the mapped risk annotations