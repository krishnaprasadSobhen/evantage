# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 12:43:46 2021

@author: Krishnaprasad Sobhen
@version: 6.0
The EVantage class controls all navigation,map rendering and data refresh operation of this project
It utilizes a variety of submodules to accomplish each stage of the route planning

The route calculation steps are:-
1.Load the following data at bootup(one time task unless live data is enabled):-
    -map boundaries of US states and counties
    -all available pandemic data
    -all available charge data
    -all available hotel data
2.Map all risk associated metrics to the counties at bootup(one time task)
3.Initialize appstate variable
    appState={
                "startPoint":None, - latitude & longitude of origin(lat,lon) -<recieved>
                "stopPoint":None, - latitude & longitude of destination -<recieved>
                "chargeRange":None, - current charge point range -<recieved>
                "hotelRange":None, - current hotel point range -<recieved>
                "searchCount":0, - search counter for app -<calculated>
                "routeObj":None, - stores raw navigation object recieved from nav module, has route and navigation stats like duration-distance-stages etc.. -<recieved>
                "routeEVLocations":None, -stores all charge point &  location range information for states through which the route passes through -<recieved>
                "routeHotels":None,- -stores all hotel & location range information for states through which the route passes through -<recieved>
                "dispEVLocations":None, - charge points and associated(lat,lon) filtered by 'chargeRange' =<calculated>
                "dispHotels":None, - hotel points and associated(lat,lon) filtered by 'hotelRange' =<calculated>
                "countiesDispData":None, - the risk data filtered for counties through which the route passes through
                "routeLocations":None, - route coordinates extracted from the raw routeObj combined with risk info=<calculated>
                "routeLine":None - a polygon version of routeObj =<calculated>
                }
4.Validate inputs recieved
5.If a valid origin and destination along with positive range parameters are recived(proximity of hotels and charge stations)
6.Calculate the fastest route using nav module
7.If a route is available utilize the pre loaded charge point,hotel,pandemic and crime risk data to compute
    -routeEVLocations - all charge points in states through which the route passes through and distance of each charge point to route
    -routeHotels - all hotels in states through which the route passes through and distance of each hotel to route
    -routeLocations - all counties through which the route passes through and pandemic+crime risk for these counties
This operation is performed only once for a given origin and destination - changes in map configuration and range parameters dont impact this information
8.From the range info captured in  routeEVLocations and routeHotels filter out points that are within requested range of hotels and charge points and stored them into
    -dispEVLocations
    -dispHotels
9.Based on the map configuration plot the route with dispEVLocations,dispHotels and routeLocations
10.Based on the information stored in dispEVLocations,dispHotels and routeObj calculate stats and pass it back to app module to be displayed


The module is written in a manner that minimizes the need to process data if no changes to a planned route are made


@functions
    -loadNewData - for live data scrapping
    -matchAppState - for deciding if the route has to be calculated again
    -updateState - updates the appState variable
    -validateInput - validates the inputs recieved from UI
    -convNumber - convert inputs from strings to numbers(floats)
    -getCount - get the current navigation count
    -updateCount -update current navigation count
    -calcRange - calculates dispHotels and dispEVLocations based on range from route
    -calcRoute - calculates the best possible route and also the risk parameters in state and counties the route passes through
    -plotRoute - plots the route information
    -findLocation - find lat,lon coordinates of given location name
    -convertTime - convert time is seconds to a string of format days,hrs,mins,secs
    -routeStats - computes route statistics for the given route - journey time,distance,number of hotel and charge stations

@version history:
    -v1 integrate charge point module with map and plot this info
    -v2 optimise routing if user input doesnt change - no recalculation for range changes
    -v3 integrated pandemic module and display data for all states 
    -v4 computed county wise distribution of pandemic data
    -v5 integrated crime risk information
    -v6 enabled live data scrapping
    
"""
import sys,os
sys.path.append(os.path.dirname(__file__))

import pandas as pd
import time
from shapely.geometry import Point
from charger.chargePoints import getEVLocations,loadEVLocations
from hotel.hotelPoints import getHotels,loadHotels
from mapMaker.mapMaker import makeMap
from riskInterface import getPandemicData,mapRiskIndex,setupRiskCounties 
from crime.crimeData import scrape_crimedata
import navigate.nav as nav



class EVantage:
    def __init__(self):
        self.originTime=time.time()
        self.startPointNm=""
        self.stopPointNm=""
        self.allPandemicData=getPandemicData()
        self.usStateMap=nav.loadMapData(fname='USStateBounds.txt') 
        self.usCounties=nav.loadMapData(fname='us-county-boundaries.json')
        self.allEVLocations=loadEVLocations()
        self.allHotels=loadHotels()
        self.countiesData=setupRiskCounties(self.allPandemicData,self.usCounties)
        self.countiesGeoData=nav.getGeoDf(self.countiesData,'poly')
        self.dispEVLocations=None
        self.dispHotels=None
        self.appState={
            "startPoint":None,
            "stopPoint":None,
            "chargeRange":None,
            "hotelRange":None,
            "searchCount":0,
            "routeObj":None,
            "routeEVLocations":None,
            "routeHotels":None,
            "dispEVLocations":None,
            "dispHotels":None,
            "countiesDispData":None,
            "routeLocations":None,
            "routeLine":None
            }
        self.bootTime=self.originTime-time.time()
        self.mapParams={
            'pandemicMap':False,
            'crimeMap':False
            }
        self.routeStatistics=[]
    def loadNewData(self):
        # load new data
        self.allHotels=loadHotels(True)
        print("Scraping hotel data completed!")
        self.allEVLocations=loadEVLocations(True)
        print("Scraping Charger location data completed!")
        scrape_crimedata()
        print("Scraping Crime data completed!")
        # this has to be manualy scrapped from the file
        # self.allPandemicData=getPandemicData(True)
        # compute new pandemic and crime risk map
        self.countiesData=setupRiskCounties(self.allPandemicData,self.usCounties)
        self.countiesGeoData=nav.getGeoDf(self.countiesData,'poly')
        
        
        
    def matchAppState(self,startPoint,stopPoint,chargeRange,hotelRange):
        if(self.appState['searchCount']==0):# first search query
            return (True,None) #(continue Navigation Flag, status update string)
        if((startPoint==self.appState['startPoint'])&(stopPoint==self.appState['stopPoint'])): # start and destination points are same
            if((chargeRange==self.appState['chargeRange'])&(hotelRange==self.appState['hotelRange'])):
                return (False,None)
            else:
                return (True,"Range") # change in range detected
        else:
            return (True,"Route")# change in route detected
    # updates appstate
    def updateState(self,startPoint,stopPoint,chargeRange,hotelRange,searchCount=0,routeObj=None,dispEVLocations=None,dispHotels=None,routeEVLocations=None,routeHotels=None,countiesDispData=None,routeLocations=None,routeLine=None):
        self.appState={
        "startPoint":startPoint,
        "stopPoint":stopPoint,
        "chargeRange":chargeRange,
        "hotelRange":hotelRange,
        "searchCount":searchCount,
        "routeObj":routeObj,
        "routeEVLocations":routeEVLocations,
        "routeHotels":routeHotels,
        "dispEVLocations":dispEVLocations,
        "dispHotels":dispHotels,
        "countiesDispData":countiesDispData,
        "routeLocations":routeLocations,
        "routeLine":routeLine
        }
    # validates input
    def validateInput(self,startPoint,stopPoint,chargeRange,hotelRange):
        if(startPoint[0][0] is None): # if no start point lat,lon was identified
                return (False,"Start point -"+startPoint[1])#(continue Navigation Flag, status update string)
        elif(stopPoint[0][0] is None): # if no stop point lat,lon was identified
            return (False,"Stop point -"+stopPoint[1])
        elif(startPoint[0][0]==stopPoint[0][0]): # if start and stop point are same
            return (False,"Origin and destination are same!")
        else:
            try:
                chargeRange=float(chargeRange.replace(",","").strip()) #  convert input range to numeric type
            except:
                return (False,"Charge point range -invalid input!") # invalid Character Encountered 
            if(chargeRange<=0):# range is negative
                return (False,"Charge point range -should be a positive number!")
            try:
                hotelRange=float(hotelRange.replace(",","").strip())
            except:
                return (False,"Hotel range -invalid input!")
            if(hotelRange<=0):
                return (False,"Hotel range -should be a positive number!")
        return (True,"Processing!")
    
    def convNumber(self,stringIp):
        return float(stringIp.replace(",","").strip())
    def getCount(self):
        return self.appState['searchCount']
    def updateCount(self):
        self.appState['searchCount']+=1
        return
    def calcRange(self,chargeRange,hotelRange):
        # filter out only charge points within given range
        dispEVLocations=self.appState["routeEVLocations"][self.appState["routeEVLocations"]['pathRange']<chargeRange]
        # filter out only hotels within given range
        dispHotels=self.appState["routeHotels"][self.appState["routeHotels"]['pathRange']<hotelRange]
        self.updateState(self.appState["startPoint"],self.appState["stopPoint"],
                        self.appState["chargeRange"],self.appState["hotelRange"],
                        self.appState["searchCount"],
                        routeObj=self.appState["routeObj"],
                        dispEVLocations=dispEVLocations,
                        dispHotels=dispHotels,
                        routeEVLocations=self.appState["routeEVLocations"],
                        routeHotels=self.appState["routeHotels"],
                        countiesDispData=self.appState["countiesDispData"],
                        routeLocations=self.appState["routeLocations"],
                        routeLine=self.appState["routeLine"])
        
    def calcRoute(self,start_point_geo,stop_point_geo):
        routeObj=nav.planRoute(start_point_geo,stop_point_geo) # compute route using nav module
        try:
            routeGeoLL=routeObj['routes'][0]['geometry']['coordinates'] # extract the actual lat lon coordinates of the route
        except:
            return (False,":/ Route not found!") # exit if no route is found
        routeLine=nav.getLineRoute(routeGeoLL) #  poly line route
        stateList=nav.getStates(routeGeoLL,self.usStateMap) # get states through which route passes through
        countiesList=nav.getCounties(routeGeoLL,self.usCounties,stateList) # get counties through which the route passes through - first filtered by stateList and further by polygon mapping
        routeEVLocations=getEVLocations(self.allEVLocations,stateList) # get charge points in states through which route passes through 
        countiesDispData=mapRiskIndex(self.countiesGeoData,stateList,countiesList) # get risk info on counties through which route passes through
        routeHotels=getHotels(self.allHotels,stateList) # get hotels in states through which route passes through 
        
        routeEVLocations=routeEVLocations.assign(pathRange=routeEVLocations.apply(lambda x: nav.minDistToRoute(Point(x['lon'],x['lat']),routeLine), axis=1))# get distance of the charge points identified in Relevant  states to the route
        routeHotels=routeHotels.assign(pathRange=routeHotels.apply(lambda x: nav.minDistToRoute(Point(x['lon'],x['lat']),routeLine), axis=1)) # get distance of the hotels identified in Relevant  states to the route

        routeLocations=pd.DataFrame(routeGeoLL).rename(columns={1:'lat',0:'lon'}) # convert route object into a data frame
        # we display the data only for counties that are part of the route -rest have annotations as tooltip
        pandemicRiskIndex,crimeRiskIndex=nav.getRouteAnnotations(routeLocations,countiesDispData) # create two datsets for pandemic and crime data to be displayed 
        routeLocations=routeLocations.assign(riskIndex=pandemicRiskIndex,crimeRiskIndex=crimeRiskIndex)
        # update appState
        self.updateState(start_point_geo,stop_point_geo,self.appState["chargeRange"],self.appState["hotelRange"],0,
                    routeObj=routeObj,dispEVLocations=routeEVLocations,
                    dispHotels=routeHotels,routeEVLocations=routeEVLocations,routeHotels=routeHotels,countiesDispData=countiesDispData,
                    routeLocations=routeLocations,routeLine=routeLine)
        return (True,"Route Found")
    # extract and share only necessary info with map module
    def plotRoute(self,pandemicDiplay=False):
        try:
            dispEVLocations=self.appState["dispEVLocations"][['lon','lat','station_name','city','ev_connector_types']]
        except:
            None
        dispHotels=self.appState["dispHotels"][['lon','lat','names','price',"latLonCat"]]
        makeMap(self.appState["routeLocations"],dispEVLocations,dispHotels,self.appState["countiesDispData"],self.startPointNm,self.stopPointNm,True,self.mapParams)

    def findLocation(self,startPoint,stopPoint,chargeRange,hotelRange,pandemicMapEnable=False,crimeMapEnable=False,webScrapping=False):
        if(webScrapping):# if web scrapping is enabled get new data
            self.loadNewData()
        start_pont_nm=startPoint.strip()
        stop_pont_nm=stopPoint.strip()
        self.mapParams={'pandemicMap':pandemicMapEnable,'crimeMap':crimeMapEnable} # parameters for map configuration
        # lat lon for start and stop point
        start_point_geo=nav.getLatLon(start_pont_nm)
        stop_point_geo=nav.getLatLon(stop_pont_nm)
        # validate all user inputs
        routingStatus=self.validateInput(start_point_geo,stop_point_geo,chargeRange,hotelRange)
        if(routingStatus[0]==False):
            return routingStatus # returns with failed status and reason for failure
        # start navigation
        self.startPointNm=start_pont_nm
        self.stopPointNm=stop_pont_nm
        # convert ranges to numeric format
        chargeRange=self.convNumber(chargeRange)
        hotelRange=self.convNumber(hotelRange)
        # obtain best execution plan to chart the route
        compState=self.matchAppState(start_point_geo[0],stop_point_geo[0],chargeRange,hotelRange)
        routingStatus=(True,"View browser,Bon Voyage!")
        t1=time.time()
        if((self.getCount()==0)|(compState[1]=="Route")): # if there are any changes to start and destination or if this is the first attempt
            # full map computation required
            self.updateState(start_point_geo[0],stop_point_geo[0],chargeRange,hotelRange)
            routingStatus=self.calcRoute(start_point_geo[0],stop_point_geo[0]) # find route
            if(routingStatus[0]==False):
                return routingStatus # if not found exit with status
            self.calcRange(chargeRange,hotelRange) # if found calculate displayed hotels,charger station based on range 
            self.plotRoute() # plot the map
            self.updateCount() # update navigation counter
        elif(compState[1]=="Range"):
            # for range change only the map and display points have to change- there is no new route required
            self.calcRange(chargeRange,hotelRange)
            self.plotRoute()
            self.updateCount()
        elif(compState[0]==False):
            # if no information has changed plot the route again - this is in case the user has closed his browser or navigation page
            self.plotRoute()
            self.updateCount()
        else:
            # this should not happen - just for debugging
            print("Unexpected event!Please try again")
        self.routeStats(time.time()-t1) # compute route calculation time and other route statistics
        return routingStatus # return routing status
    # return time in a readable format from seconds input
    def convertTime(self,seconds): 
        seconds=abs(seconds)
        days = seconds // (24 * 3600)
        hours = seconds % (24 * 3600)
        hour = hours // 3600
        hours %= 3600
        minutes = hours // 60
        hours %= 60
        seconds = hours
        output=""
        if(days>0):
            output=output+str(round(days))+" Day "
        if(hour>0):
            output=output+str(round(hour))+" Hour "
        if(minutes>0):
            output=output+str(round(minutes))+" Min "
        if(seconds>0):
            output=output+str(round(seconds))+" Sec "
        return output
    def routeStats(self,routeTime):
        distance="Distance: "+str(round(self.appState['routeObj']['routes'][0]['distance']/1609,2))+"mile(s)" # driving distance from  route object
        travelTime="Driving Time: "+self.convertTime(int(self.appState['routeObj']['routes'][0]['duration'])) # driving time from route object
        noChargePoints="No. Charging stations found: "+str(self.appState['dispEVLocations'].shape[0]) if(~self.appState['dispEVLocations'].empty) else "No charging stations found!" # number of charge points in range
        noHotels="No. Hotels found: "+str(self.appState['dispHotels'].shape[0]) if(~self.appState['dispHotels'].empty) else "No hotel partners on your route!" # number of hotels in range
        routingTime="Route calculation time: "+self.convertTime(routeTime) # time taken to compute route
        self.routeStatistics="\n".join([distance,travelTime,noChargePoints,noHotels,routingTime]) # concatnate with \n delimiter for displaying as status
        return
   
        
         