# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 14:20:15 2021

@author: 
    Krishnaprasd Sobhen(ksobhen)
    Tapasya Maji(tmaji)
    Yoshinori Ushiyama(yushiyam)
@version: 6.0

This module scrapes and handles all charger network related info

@functions:
    -getNewData - loads new charger location data from nrel.gov/api/alt-fuel-stations using an api call and key
    -getStateMap - returns the charge location data for given state list
    -getEVLocations - gets charge point locations with getStateMap
    -loadEVLocations - load previously collected info or initiate getNewData
    
"""
import json
import pandas as pd
import requests
import time

import os
path=os.path.dirname(__file__)
def getNewData(overwrite=False):
    with open(path+"/apiKey.txt", 'r') as file:
        apikey=file.read().strip()
    data_json = requests.get('https://developer.nrel.gov/api/alt-fuel-stations/v1.json?api_key='+apikey+'&fuel_type=ELEC&country=US&limit=all')
    time.sleep(20)
    data=data_json.json()
    if(overwrite):
        with open(os.path.join(path,'./data/EVChargePts.json'), 'w') as file:
             file.write(json.dumps(data))
    return data

def getStateMap(stateList,data):
    stateMap={'name': ['Alaska','Alabama','Arkansas','Arizona','California','Colorado','Connecticut','District of Columbia','Delaware','Florida','Georgia','Hawaii','Iowa','Idaho','Illinois','Indiana','Kansas','Kentucky','Louisiana','Massachusetts','Maryland','Maine','Michigan','Minnesota','Missouri','Mississippi','Montana','North Carolina','North Dakota','Nebraska','New Hampshire','New Jersey','New Mexico','Nevada','New York','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Virginia','Vermont','Washington','Wisconsin','West Virginia','Wyoming'],
     'code': ['AK','AL','AR','AZ','CA','CO','CT','DC','DE','FL','GA','HI','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VA','VT','WA','WI','WV','WY']
    }
    stateMap=pd.DataFrame(stateMap)
    stateMap=stateMap[stateMap['name'].isin(stateList)]
    return data[data['state'].isin(stateMap['code'])]

def getEVLocations(data,stateList):
    data= getStateMap(stateList,data)
    return data

def loadEVLocations(newDataFlag=False,overwrite=True,fname='EVChargePts.json'):
    if(newDataFlag):
        data=getNewData(overwrite)
    else:
        with open(path+"./data/"+fname,encoding='utf-8') as f:
            data = json.load(f)
    data=pd.DataFrame(data['fuel_stations'])
    data=data[(data['access_code']=='public')&(data['status_code']!='T')&(data['geocode_status']=='GPS')]
    data=data[['id',
    'station_name',
    'street_address',
    'intersection_directions',
    'city',
    'state',
    'zip',
    'plus4',
    'access_detail_code',
    'status_code',
    'cards_accepted',
    'latitude',
    'longitude',
    'ev_pricing_fr',
    'ev_connector_types'
    ]].rename(columns={'latitude':'lat','longitude':'lon'})
    return data

