# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 16:31:49 2021

@author: Krishnaprasad Sobhen
@version: 3.0

This module collects and integrates all county level data - risk data 

@functions:
    -getStateMap - maps from state names to state code for a given state name list
    -getPandemicData - loads new pandemic data if a live connection is requested
    -mapRiskIndex - maps risk index from a given data set of all counties to two new columns(pandemic & crime risk) for supplied county+state list
    -matchState - maps from state names to state code for a given state name list 
    -setupRiskCounties - for all the counties in US compute simplified shape polygons and associated risk metrics

@version history:
    -v1-integrated pandemic module and tested for state distribution
    -v2-pre loading support for all counties implemented
    -v3-integrated crime module

"""



from pandemic.nyt_pandemic_data import pandemicRisk,loadPandemicData
from pandemic.nyt_pandemic_selenium_states_counties import pandemicScrapper

from crime.crimeData import crime_rate

from shapely.geometry import shape
import pandas as pd

import time 

def getStateMap(stateList):
    stateMap={'name': ['Alaska','Alabama','Arkansas','Arizona','California','Colorado','Connecticut','District of Columbia','Delaware','Florida','Georgia','Hawaii','Iowa','Idaho','Illinois','Indiana','Kansas','Kentucky','Louisiana','Massachusetts','Maryland','Maine','Michigan','Minnesota','Missouri','Mississippi','Montana','North Carolina','North Dakota','Nebraska','New Hampshire','New Jersey','New Mexico','Nevada','New York','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Virginia','Vermont','Washington','Wisconsin','West Virginia','Wyoming'],
     'code': ['AK','AL','AR','AZ','CA','CO','CT','DC','DE','FL','GA','HI','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VA','VT','WA','WI','WV','WY']
    }
    stateMap=pd.DataFrame(stateMap)
    stateMap=stateMap[stateMap['name'].isin(stateList)]
    return stateMap['code'].values

def getPandemicData(newDataFlag=False):
    if(newDataFlag):
        pandemicScrapper()
    return loadPandemicData()


def mapRiskIndex(data,stateList,countiesList):
    stateList=getStateMap(stateList)
    countiesList=pd.DataFrame(countiesList)
    countiesList["stateCode"]=countiesList.apply(lambda row:matchState(row['state']),axis=1)
    countiesList['matchFlag']=1
    data_final=pd.merge(data,countiesList,  how='left', left_on=['stateCode','county'], right_on = ['stateCode','county']).rename(columns={'state_x':'state'})
    data_final['disp_risk_index']=data_final.apply(lambda row:row['riskIndex'] if row['matchFlag']==1 else None,axis=1)
    data_final['disp_crime_index']=data_final.apply(lambda row:row['crimeIndex'] if row['matchFlag']==1 else None,axis=1)
    data_final=data_final[['state','county', 'poly','stateCode','riskIndex','crimeIndex','disp_risk_index','disp_crime_index']]
    return data_final


def matchState(stateName):
    stateMap={'Alaska': 'AK',
 'Alabama': 'AL',
 'Arkansas': 'AR',
 'Arizona': 'AZ',
 'California': 'CA',
 'Colorado': 'CO',
 'Connecticut': 'CT',
 'District of Columbia': 'DC',
 'Delaware': 'DE',
 'Florida': 'FL',
 'Georgia': 'GA',
 'Hawaii': 'HI',
 'Iowa': 'IA',
 'Idaho': 'ID',
 'Illinois': 'IL',
 'Indiana': 'IN',
 'Kansas': 'KS',
 'Kentucky': 'KY',
 'Louisiana': 'LA',
 'Massachusetts': 'MA',
 'Maryland': 'MD',
 'Maine': 'ME',
 'Michigan': 'MI',
 'Minnesota': 'MN',
 'Missouri': 'MO',
 'Mississippi': 'MS',
 'Montana': 'MT',
 'North Carolina': 'NC',
 'North Dakota': 'ND',
 'Nebraska': 'NE',
 'New Hampshire': 'NH',
 'New Jersey': 'NJ',
 'New Mexico': 'NM',
 'Nevada': 'NV',
 'New York': 'NY',
 'Ohio': 'OH',
 'Oklahoma': 'OK',
 'Oregon': 'OR',
 'Pennsylvania': 'PA',
 'Rhode Island': 'RI',
 'South Carolina': 'SC',
 'South Dakota': 'SD',
 'Tennessee': 'TN',
 'Texas': 'TX',
 'Utah': 'UT',
 'Virginia': 'VA',
 'Vermont': 'VT',
 'Washington': 'WA',
 'Wisconsin': 'WI',
 'West Virginia': 'WV',
 'Wyoming': 'WY',
 'Puerto Rico':'PR',
 'American Samoa':'AS'}
    x=""
    try:
        x=stateMap[stateName]
    except:
        x="UNKNOWN"
    return x

def setupRiskCounties(data,usCounties,epsilon=0.00005):    
    # epsilon is the curve smoothening parameter to reduce computation
    # ranges from 1-most smooth to 0-Least  smooth
    stateMap=['Alaska','Alabama','Arkansas','Arizona','California','Colorado','Connecticut','District of Columbia','Delaware','Florida','Georgia','Hawaii','Iowa','Idaho','Illinois','Indiana','Kansas','Kentucky','Louisiana','Massachusetts','Maryland','Maine','Michigan','Minnesota','Missouri','Mississippi','Montana','North Carolina','North Dakota','Nebraska','New Hampshire','New Jersey','New Mexico','Nevada','New York','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Virginia','Vermont','Washington','Wisconsin','West Virginia','Wyoming']
    stateList=getStateMap(stateMap)
    data_filt1=pd.DataFrame(pandemicRisk(stateList, data))
    data_filt2=pd.DataFrame(crime_rate(stateList)).rename(columns={'Crime Index':'crimeIndex'})
    extractStates=[]
    for county in usCounties:
        extractStates.append({
            "state":county['fields']['state_name'],
            "county":county['fields']['name'],
            "poly":shape(county['fields']['geo_shape']).simplify(epsilon,False) # simplify county shapes
            })
    extractStates=pd.DataFrame(extractStates)
    extractStates["stateCode"]=extractStates.apply(lambda row:matchState(row['state']),axis=1)
    # merge on county name and state to add risk info in two steps - left join since all counties are to be captured
    data_final=pd.merge(extractStates, data_filt1,  how='left', left_on=['stateCode','county'], right_on = ['state','countyName'])[['state_x', 'county', 'poly', 'stateCode','riskIndex']]
    data_final=pd.merge(data_final, data_filt2,  how='left', left_on=['stateCode','county'], right_on = ['State','CountyName'])[['state_x', 'county', 'poly', 'stateCode','riskIndex','crimeIndex']]
    # exclude states not part of continental US
    data_final=data_final[((data_final['stateCode']!='AK')& # alaska is also excluded 
                       (data_final['stateCode']!='PR')&
                       (data_final['stateCode']!='HI')&
                       (data_final['stateCode']!='AS')&
                       (data_final['stateCode']!="UNKNOWN"))
                      ]
    data_final[['riskIndex']]=data_final[['riskIndex']].fillna(0) # fill empty values with zero
    data_final[['crimeIndex']]=data_final[['crimeIndex']].fillna(0)
    data_final[['disp_risk_index']]=0 # setup for display values
    data_final[['disp_crime_index']]=0
    return data_final.rename(columns={'state_x':'state'})
