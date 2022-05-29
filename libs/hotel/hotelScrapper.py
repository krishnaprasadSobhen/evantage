# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 21:21:21 2021

@author: 
    Krishnaprasd Sobhen(ksobhen)
    Tapasya Maji(tmaji)
    Yoshinori Ushiyama(yushiyam)
@version:1.0

This is the webscrapping module for hotel data
1.It obtains the hotel names,rates and addresses from bookings.com via selenium
2.It obtains the location info with the help of Nominatim api service of geopy module
3.A rate limiter is also utilized here to prevent the nominatim service from failing under frequent requests

@functions:
    -fetchPages - master module that :
                    -launches the browser
                    -navigates to hotel availablity in USA for current data
                    -scrapes each page for every available page
    
    -findNames- from a scrapped page determine all hotel names 
    -findlocation-from a scrapped page determine all hotel address
    -findprice - from a scrapped page determine all hotel prices
    -getAddress- from scrapped address in a page determine all  lat lon through api calls to nominatim

    
    
"""
import sys,os
sys.path.append(os.path.dirname(__file__))
path=os.path.dirname(__file__)

from selenium import webdriver
import pandas as pd
import time
from selenium.webdriver.support.ui import Select
# from selenium.webdriver.chrome.options import Options

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

def getAddress(searchStr):
    locator = Nominatim(user_agent="EVantage")
    locaterRateLimited = RateLimiter(locator.geocode, min_delay_seconds=1) # rate limiter set to 1 sec
    latLon=[]
    for i in searchStr:
        # rate limited to 1 search request per sec - https://operations.osmfoundation.org/policies/nominatim/
        location = locaterRateLimited(i['searchStr1'])
        if(location is not None):
            latLon.append((location.latitude, location.longitude,location.address.split(",")[-3].strip(),"D")) # D-Deep 
        else:
            location = locaterRateLimited(i['searchStr2'])
            if(location is not None):
                latLon.append((location.latitude, location.longitude,location.address.split(",")[-3].strip(),"H")) # H-HighLevel - if a deep coordinateis not found look for next lavel in address
            else:
                latLon.append((None,None,None,"N"))# N - No Match
    return latLon

def findNames(hotels):
    goFlag=True
    counter=1
    names=[]
    foundagain=False
    while(goFlag):
        try:
            hotels.find_element_by_xpath('./div['+str(counter)+']')
        except:
            break# seach for ad
        if(hotels.find_element_by_xpath('./div['+str(counter)+']').text.find('Sign in')!=-1):
            if(foundagain==True):# second ad at the bottom of page
                break
            foundagain=True
            counter+=1
            continue
        try:# extract name data
            names.append(hotels.find_element_by_xpath('./div['+str(counter)+']/div[2]/div[1]/div[1]/div[1]').text)
        except:
            "do nothing- skips ad listing"
        counter+=1
    return names

def findlocation(hotels):
    goFlag=True
    counter=1
    locations=[]
    foundagain=False
    while(goFlag):
        try:
            hotels.find_element_by_xpath('./div['+str(counter)+']')
        except:
            break
        if(hotels.find_element_by_xpath('./div['+str(counter)+']').text.find('Sign in')!=-1):
            if(foundagain==True):
                break
            foundagain=True
            counter+=1
            continue
        try:
            locations.append(hotels.find_element_by_xpath('./div['+str(counter)+']/div[2]/div[1]/div[1]/div[2]/a[1]').text)
        except:
            "do nothing- skips ad listing"
        counter+=1
    return locations

def findprice(hotels):
    goFlag=True
    counter=1
    prices=[]
    price=""
    # currency="₹"
    currency="$"
    foundagain=False
    while(goFlag):
        try:
            hotels.find_element_by_xpath('./div['+str(counter)+']')
        except:
            goFlag=False
            break
        if(hotels.find_element_by_xpath('./div['+str(counter)+']').text.find('Sign in')!=-1):
            if(foundagain==True):
                break
            foundagain=True
            counter+=1
            continue
        try:
            price=hotels.find_element_by_xpath('./div['+str(counter)+']//div[contains(text(),"'+currency+'") and not(contains(@class,"strikethrough")) and not(contains(@class,"taxes"))]').text
            if(price==''):
                price=hotels.find_element_by_xpath('./div['+str(counter)+']//label[contains(text(),"'+currency+'") and not(contains(@class,"strikethrough")) and not(contains(@class,"taxes"))]').text
            prices.append(price)
        except:
            "do nothing- skips ad listing"
        counter+=1
    return prices

def fetchPages():
    # options = Options()
    # options.add_argument('--headless')
    # driver = webdriver.Chrome(os.path.join(path,'../chromedriver.exe'), options=options)
    driver = webdriver.Chrome(os.path.join(path,'../chromedriver.exe'))
    pages=[]
    driver.get('https://www.booking.com') # opens site
    time.sleep(10)
    driver.find_elements_by_xpath("//input[@id='ss']")[0].send_keys("United States") # enters search string United States"
    time.sleep(1)
    
    sel=Select(driver.find_elements_by_xpath("//form[@id='frm']/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/select[1]")[0])
    sel.select_by_index(1) # always current month
    time.sleep(1)
    driver.find_element_by_xpath('/html/body/div[2]/div/div/div[2]/form/div[1]/div[2]/div[1]/div[3]/div/div').click()
    time.sleep(1)
    # click current date
    driver.find_element_by_xpath('//*[@id="frm"]/div[1]/div[2]/div[2]/div/div/div[3]/div[1]/table/tbody//span[contains(text(),'+str(time.localtime().tm_mday)+')]').click()
    time.sleep(1)
    # click search
    driver.find_element_by_xpath('//*[@id="frm"]/div[1]/div[4]/div[2]/button').click()
    time.sleep(10)
    goFlag=True
    page_no=1# page identifier
    countItem=1# item in page
    while(goFlag):
        countItem=1
        if(page_no!=1):
            try:# search for next button
                driver.find_element_by_xpath('//li[@class="bui-pagination__item bui-pagination__next-arrow"]').click()
            except:
                goFlag=False
                break
        time.sleep(5) # load hotels
        hotels=driver.find_element_by_xpath('//div[@id="hotellist_inner"]')
        # get name,address ,location and prices 
        pages.append({
            'pg_no':page_no,
            'names':findNames(hotels),
            'locations':findlocation(hotels),
            'prices':findprice(hotels)
        })
        countItem+=len(pages[page_no-1]['names'])
        page_no+=1
    data_final={
    'names':[],
    'address':[],
    'price':[],
    'lat':[],
    'lon':[],
    'state':[],
    'latLonCat':[]
    }
    
    for page in pages:
        names=[]
        locations=[]
        lat=[]
        lon=[]
        latLonCat=[]
        state=[]
        price=[]
        for i in page['names']:
            names.append(i.split('\n')[0])
        for i in page['locations']:
            locations.append(i.split('\n')[0])
        namesSearch=[x.lower().replace('&','').replace(',',' ').replace('-',' ').replace('  ',' ') for x in names]
        locationsSearch=[x.replace(' Show on map','').lower().replace('&','').replace('-',' ').replace('  ',' ') for x in locations]
        searchStr=[]
        for index,name in enumerate(namesSearch):# create a two leavel search string array from names and locations
            searchStr.append({'searchStr1':(name+","+locationsSearch[index]+",USA"),'searchStr2':(locationsSearch[index]+",USA")})
        latLonAddr=getAddress(searchStr) # find location coordinates
        # convert all the data into a dict of lists
        for point in latLonAddr:
            lat.append(point[0])
            lon.append(point[1])
            state.append(point[2])
            latLonCat.append(point[3])
        data_final['names'].extend(names)
        data_final['address'].extend(page['locations']) # got to fix this
        data_final['price'].extend(page['prices'])
        data_final['lat'].extend(lat)
        data_final['lon'].extend(lon)
        data_final['state'].extend(state)
        data_final['latLonCat'].extend(latLonCat)
    data_final=pd.DataFrame(data_final) # convert and return a dataframe of the dict output
    driver.quit()
    return data_final
