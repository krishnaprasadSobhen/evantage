# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 23:57:38 2021

@author: 
    Krishnaprasd Sobhen(ksobhen)
    Tapasya Maji(tmaji)
    Yoshinori Ushiyama(yushiyam)
    

@version:1.0

This module loads the scrapped hotel data for interfacing with the master module

@functions:
    -getNewData-connects to data scrapping module and loads new data when prompted - it also writes the loaded data if overwriteflag is set 
    -getHotels-filters hotel data for a given state list from input hotels data set
    -loadHotels-controls getNewData and can supply existing data or new data to requester
"""
import pandas as pd
import sys,os


sys.path.append(os.path.dirname(__file__))
path=os.path.dirname(__file__)+"./data/"

from hotelScrapper import fetchPages

def getNewData(overwrite=False):
    data=fetchPages()
    if(overwrite):
        data.to_excel(path+"Hotel data lat lon.xlsx",index=False)
    return data

def getHotels(data,stateList):
    data=data[data['state'].isin(stateList)]
    return data

def loadHotels(newDataFlag=False,overwrite=False,fname='Hotel data lat lon.xlsx'):
    if(newDataFlag):
        data=getNewData(overwrite)
    else:
        data=pd.read_excel(path+fname)
    return data

