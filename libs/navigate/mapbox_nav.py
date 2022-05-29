# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 13:09:02 2021

@author: 
    Krishnaprasd Sobhen(ksobhen)
    Tapasya Maji(tmaji)
    Yoshinori Ushiyama(yushiyam)
@version: 2.0

This module makes api calls to mapbox driving services to collect fastest route information for a given par of origin-destination coordinates

@functions:
    -getKey- retrieves api key stored in mapBoxKey.txt
    -getRouteObject fetched the route object from mapbox driving service
@version history:
    -v1-implimented getRouteObject to obtain fastest from origin to destination
    -v2-implimented getKey to make the key easily replaceable
    
"""

import requests
import json

import os
path=os.path.dirname(__file__)

def getKey(fileName='./mapBoxKey.txt'):
    with open(path+fileName, 'r') as file:
        return file.read().strip()

def getRouteObject(start_point_geo,stop_point_geo,key="pk.eyJ1Ijoia3pvYmhlbiIsImEiOiJja2x5aG94ZW4wNDNsMm5vOWZ1Y3N4cGFvIn0.pJdGrPvaiZP-wQ-R2Avy3Q"):
    latLonStr=','.join(map(str,start_point_geo))+';'+','.join(map(str,stop_point_geo))
    response = requests.get("https://api.mapbox.com/directions/v5/mapbox/driving/"+latLonStr+"?alternatives=false&geometries=geojson&overview=full&annotations=duration&access_token="+key)
    data=json.loads(response.content)
    return data

    
