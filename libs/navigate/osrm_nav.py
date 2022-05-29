# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 13:09:02 2021


@author: 
    Krishnaprasd Sobhen(ksobhen)
    Tapasya Maji(tmaji)
    Yoshinori Ushiyama(yushiyam)
@version: 2.0

This module makes api calls to Open Source Routing Machine's(OSRM) driving & nearest services to collect fastest route information for a given par of origin-destination coordinates

@functions:
    -getNearest- retrieves nearest road to a given lat lon point
    -getRouteObject- fetches the route object from OSRM driving service
@version history:
    -v1-implimented getNearest
    -v2-implimented getRouteObject based on inputs from getNearest to obtain fastest from origin to destination
"""

import requests
import json

def getNearest(latLon):
    response = requests.get("http://router.project-osrm.org/nearest/v1/driving/"+(','.join(latLon))+'?number=1')
    print("Nearest point API status : ",response.status_code) # print response code
    data=json.loads(response.content)
    # print(data)
    return data['waypoints'][0]['location']

def getRouteObject(start_point_geo,stop_point_geo,level="full"):
    latLonStr=','.join(map(str,start_point_geo))+';'+','.join(map(str,stop_point_geo))
    response = requests.get("http://router.project-osrm.org/route/v1/driving/"+latLonStr+"?alternatives=false&geometries=geojson&overview="+level+"&annotations=false")
    data=json.loads(response.content)
    # print(data)
    return data
