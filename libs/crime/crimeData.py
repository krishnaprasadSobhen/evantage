#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 17:17:19 2021

@author: 
    Tapasya Maji(tmaji)
    Yoshinori Ushiyama(yushiyam)
    Krishnaprasd Sobhen(ksobhen)
"""
import os
path=os.path.dirname(__file__)+"./data/"

from urllib.request import Request, urlopen  
from bs4 import BeautifulSoup
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import csv

#--------------------------------------------------------------------------
#Scraping Crime Data using BeautifulSoup
#--------------------------------------------------------------------------
def scrape_crimedata():
    site= "https://ucr.fbi.gov/crime-in-the-u.s/2019/crime-in-the-u.s.-2019/topic-pages/tables/table-6"

    hdr = {'User-Agent': 'Chrome/88.0.4324.190'}
 
    req = Request(site,headers=hdr)
    page = urlopen(req)
    bsyc = BeautifulSoup(page.read(), "lxml")
    fout = open(path+'CRIME DATA.txt', 'wt',encoding='utf-8')
    fout.write(str(bsyc))
    fout.close()
   
    table_container = bsyc.findAll('div',
                                   { "id" : "table-data-container" } )
    table_list1=table_container[0].findNext('table')
    table_head=table_list1.findNext('thead') # parse this to get a list of headers - lets call it h1
    table_body=table_list1.findNext('tbody')
    table_rows=table_body.findAll('tr')

#--------------------------------------------------------------------------
#Scraping the data from website to a list of dicts
#--------------------------------------------------------------------------
    curr_pos=0# loop control variable
    full_data=[]
    state_name=""
    county_name=""

    fout1 = open(path+'crime_raw_data.txt', 'wt', encoding = 'utf-8') 

    while(curr_pos<len(table_rows)):
        table_row=table_rows[curr_pos] # loop control variable
        th_list=table_row.findAll('th')
        if(len(th_list)==2):
            state_name=th_list[0].findNext("b").text
            skip=th_list[0].get("rowspan") # this tells you to look at row to find metrics
        
            county_row=table_rows[curr_pos+1]
            county_name=county_row.findNext("th").text.strip()
        
            curr_pos=curr_pos+int(skip)-1
        
        elif(len(th_list)==1):
            x=[]
            for c in table_row.children:
                try:
                    x.append((c.text).strip())
                except:
                    continue
            full_data.append({"state_name":state_name,"county_name":county_name,"values":x,})
            curr_pos+=1

    fout1.write(str(full_data))
    fout1.close()

    return(full_data)

#-------------------------------------------------------------------------------
#Scanning through the list of dicts created for State, their respective counties 
#and the crime rate in those counties and get a cleaned list of lists
#writing it to crime_clean_data.txt
#--------------------------------------------------------------------------------

def loadCrimeData():
    full_data = scrape_crimedata()
    fout = open(path+'crime_clean_data.txt', 'wt', encoding = 'utf-8')
    pos = 0
    crime_list =[]
    while(pos<len(full_data)):
        state_name1 = full_data[pos]['state_name']
        county_name1 = full_data[pos]['county_name']
        values1 = full_data[pos]['values']
        if(state_name1 == ''):
            stat1 = 'Unknown'
            cnty1 = county_name1.split(",")
            pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
            while(pos2<len(cnty1)):
                if(len(cnty1[pos2].strip().split(' ')) == 1):
                    crime_list.append(stat1.strip() + ":" + cnty1[pos2].strip() + ":" + listToStr)
                else:
                    cnty2 = cnty1[pos2].strip().split(' ')
                    pos3 =0
                    while(pos3<len(cnty2)):
                        if ((cnty2[pos3] != 'Includes') & (cnty2[pos3] != 'and') & (cnty2[pos3] != ',')
                            & (cnty2[pos3] != 'Counties') & (cnty2[pos3] != 'County')
                            & (cnty2[pos3] != 'Municipios') & (cnty2[pos3] != 'Municipality')
                            & (cnty2[pos3] != 'Counties3') & (cnty2[pos3] != 'County4')):
                            crime_list.append(stat1.strip() + ":" + cnty2[pos3].strip()+ ":"+ listToStr)
                        pos3+=1
                pos2+=1

#Few of the M.S.A.s comprises of counties from multiple states
#For such M.S.A.s, the counties as per their respective states are extracted
  
        elif(state_name1 == 'Watertown-Fort Drum, NY M.S.A.'):
            if(county_name1 == 'Includes Jefferson County'):
                stat1 = state_name1.split(',')
                stat2 = stat1[1].split(" ")
                cnty1 = county_name1.strip().split(" ")
                # print(cnty1[1])
                pos2 = 0
                v1=[]
                x = 2
                while(x<len(values1)):
                    v = values1[x].split(' ')
                    for k in v:
                        v1.append(k)
                    x+=1
                    listToStr = ':'.join(map(str, v1))
                while(pos2<len(cnty1)):
                    if ((cnty1[pos2] != 'Includes') & (cnty1[pos2] != 'County')):
                        crime_list.append(stat2[1].strip() + ":" + cnty1[pos2].strip() + ":" + listToStr)
                    pos2+=1
                  
        elif(state_name1 == 'Alexandria, LA M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
            crime_list.append(stat2[1].strip() + ":" + cnty1[1].strip() + ":" + listToStr)
            crime_list.append(stat2[1].strip() + ":" + cnty1[3].strip()+' '+cnty1[4].strip()+ ":" + listToStr)
        
        elif(state_name1 == 'Baltimore-Columbia-Towson, MD M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
        
            crime_list.append(stat2[1].strip() + ":" + cnty1[1].strip()+' '+cnty1[2].strip(',')+ ":" + listToStr)
            crime_list.append(stat2[1].strip() + ":" + cnty1[3].strip(',') + ":" + listToStr)
            crime_list.append(stat2[1].strip() + ":" + cnty1[4].strip(',') + ":" + listToStr)
            crime_list.append(stat2[1].strip() + ":" + cnty1[5].strip(',') + ":" + listToStr)
            crime_list.append(stat2[1].strip() + ":" + cnty1[6].strip(',') + ":" + listToStr)
            crime_list.append(stat2[1].strip() + ":" + cnty1[8].strip(',')+' '+cnty1[9].strip()+ ":" + listToStr)
            crime_list.append(stat2[1].strip() + ":" + cnty1[12].strip()+' '+cnty1[13].strip()+ ":" + listToStr)
        
        elif(state_name1 == 'Baton Rouge, LA M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
        
            crime_list.append(stat2[1].strip() + ":" + cnty1[1].strip(',') + ":" + listToStr)
            crime_list.append(stat2[1].strip() + ":" + cnty1[2].strip(',') + ":" + listToStr)
            crime_list.append(stat2[1].strip() + ":" + cnty1[3].strip()+' '+cnty1[4].strip(',')+' '+cnty1[5].strip(',')+ ":" + listToStr)
            crime_list.append(stat2[1].strip() + ":" + cnty1[6].strip()+' '+cnty1[7].strip(',')+ ":" + listToStr)
            crime_list.append(stat2[1].strip() + ":" + cnty1[8].strip(',') + ":" + listToStr)
            crime_list.append(stat2[1].strip() + ":" + cnty1[9].strip(',') + ":" + listToStr)
            crime_list.append(stat2[1].strip() + ":" + cnty1[10].strip()+' '+cnty1[11].strip(',')+ ":" + listToStr)
            crime_list.append(stat2[1].strip() + ":" + cnty1[12].strip()+' '+cnty1[13].strip(',')+ ":" + listToStr)
            crime_list.append(stat2[1].strip() + ":" + cnty1[14].strip()+' '+cnty1[15].strip(',')+' '+cnty1[16].strip(',')+ ":" + listToStr)
            crime_list.append(stat2[1].strip() + ":" + cnty1[18].strip()+' '+cnty1[19].strip(',')+' '+cnty1[20].strip(',')+ ":" + listToStr)
    
        elif(state_name1 == 'Grand Forks, ND-MN M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
            crime_list.append(stat3[1].strip() + ":" + cnty1[1].strip() + ":" + listToStr)
            crime_list.append(stat3[0].strip() + ":" + cnty1[5].strip()+' '+cnty1[6].strip()+ ":" + listToStr)
        
        elif(state_name1 == 'Augusta-Richmond County, GA-SC M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
        
            pos4 = 0
        
            while(pos4<len(cnty1)):
                if((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='Counties,') & (pos4<8)):
                    crime_list.append(stat3[0].strip() + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                elif ((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='GA3') & (cnty1[pos4]!='SC')
                      & (cnty1[pos4]!='Counties,') & (pos4>=8)):
                    crime_list.append(stat3[1].strip() + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                pos4+=1
  
        elif(state_name1 == 'Boston-Cambridge-Newton, MA-NH M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
                  
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[5].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[7].strip(',') + ":" + listToStr)
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[10].strip(',') + ":" + listToStr)
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[11].split('-')[1].strip(',') + ":" + listToStr)   

        elif(state_name1 == 'Cape Girardeau, MO-IL M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
                  
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[1].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[5].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[7].strip(',') + ' ' + cnty1[8].strip(',') + ":" + listToStr)
                        
        elif(state_name1 == 'Chattanooga, TN-GA M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
            pos4 = 0
        
            while(pos4<len(cnty1)):
                if((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='Counties,') & (pos4<5)):
                    crime_list.append(stat3[1].strip('3') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                elif ((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='GA3') & (cnty1[pos4]!='TN')
                      & (cnty1[pos4]!='Counties,') & (pos4>=5)):
                    crime_list.append(stat3[0].strip() + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                pos4+=1
            
        elif(state_name1 == 'Cincinnati, OH-KY-IN M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
            pos4 = 0
        
            while(pos4<len(cnty1)):
                if((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='Counties,') & (pos4<6)):
                    crime_list.append(stat3[2].strip(';') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                elif ((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='IN;') & (cnty1[pos4]!='KY;')
                      & (cnty1[pos4]!='Counties,') & (pos4>=6) &(pos4<18)):
                    crime_list.append(stat3[1].strip(';') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                elif ((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='KY;') & (cnty1[pos4]!='OH')
                      & (cnty1[pos4]!='Counties,') & (pos4>=18)):
                    crime_list.append(stat3[0].strip(';') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)

                pos4+=1
        
        elif(state_name1 == 'Clarksville, TN-KY M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
            pos4 = 0
        
            while(pos4<len(cnty1)):
                if((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='Counties,') & (pos4<5)):
                    crime_list.append(stat3[1].strip('3') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                elif ((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='KY') & (cnty1[pos4]!='TN')
                      & (cnty1[pos4]!='Counties,') & (pos4>=5)):
                    crime_list.append(stat3[0].strip() + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                pos4+=1

        elif(state_name1 == 'Cumberland, MD-WV M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
                  
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[1].strip(',') + ":" + listToStr)
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[5].strip(',') + ":" + listToStr)
      
        elif(state_name1 == 'Davenport-Moline-Rock Island, IA-IL M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
                  
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[1].strip(',') + ":" + listToStr)
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[2].strip(',') + ":" + listToStr)
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[4].strip(',') +' '+ cnty1[5].strip(',')+ ":" + listToStr)        
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[9].strip(',') + ":" + listToStr)

        elif(state_name1 == 'Duluth, MN-WI M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
                  
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[1].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[2].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[4].strip(',') +' '+ cnty1[5].strip('3')+ ":" + listToStr)        
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[9].strip(',') + ":" + listToStr)

        elif(state_name1 == 'Evansville, IN-KY M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
                  
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[1].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[2].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[4].strip(',') + ":" + listToStr)       
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[8].strip(',') + ":" + listToStr)

        elif(state_name1 == 'Fargo, ND-MN M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
                  
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[1].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[5].strip(',') + ":" + listToStr)

        elif(state_name1 == 'Fort Smith, AR-OK M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
                  
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[1].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[2].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[4].strip(',') + ":" + listToStr)
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[8].strip(',') + ":" + listToStr)

        elif(state_name1 == 'Huntington-Ashland, WV-KY-OH M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))

            pos4 = 0
        
            while(pos4<len(cnty1)):
                if((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='Counties,') & (pos4<6)):
                    crime_list.append(stat3[1].strip(';') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                elif ((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='OH;') & (cnty1[pos4]!='KY;')
                      & (cnty1[pos4]!='Counties,') & (cnty1[pos4]!='County')& (pos4>=6) &(pos4<9)):
                    crime_list.append(stat3[2].strip(';') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                elif ((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='WV') & (cnty1[pos4]!='OH;')
                      & (cnty1[pos4]!='Counties,') & (pos4>=9)):
                    crime_list.append(stat3[0].strip(';') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)

                pos4+=1

        elif(state_name1 == 'La Crosse-Onalaska, WI-MN M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
                  
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[1].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[5].strip(',')+' '+cnty1[6].strip(',') + ":" + listToStr)

        elif(state_name1 == 'Kingsport-Bristol, TN-VA M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
                  
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[1].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[3].strip(',') + ":" + listToStr)
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[7].strip(',') + ":" + listToStr)        
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[12].strip(',')+' '+cnty1[13].strip(',') + ":" + listToStr)

        elif(state_name1 == 'Lewiston, ID-WA M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
                  
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[1].strip(',')+' '+cnty1[2].strip(',') + ":" + listToStr)
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[6].strip(',') + ":" + listToStr)

        elif(state_name1 == 'Logan, UT-ID M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
                  
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[1].strip(',')+ ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[5].strip(',') + ":" + listToStr)

        elif(state_name1 == 'Louisville/Jefferson County, KY-IN M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))

            pos4 = 0
        
            while(pos4<len(cnty1)):
                if((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='Counties,') & (pos4<7)):
                    crime_list.append(stat3[1].strip('3') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                elif ((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='KY') & (cnty1[pos4]!='IN')
                      & (cnty1[pos4]!='Counties,') & (pos4>=8)):
                    crime_list.append(stat3[0].strip() + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                pos4+=1
                  
        elif(state_name1 == 'Memphis, TN-MS-AR M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))

            pos4 = 0
        
            while(pos4<len(cnty1)):
                if((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='Counties,')& (cnty1[pos4]!='County') & (pos4<3)):
                    crime_list.append(stat3[2].strip(';') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                elif ((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='AR;') & (cnty1[pos4]!='MS;')
                      & (cnty1[pos4]!='Counties,') & (cnty1[pos4]!='County')& (pos4>=3) &(pos4<10)):
                    crime_list.append(stat3[1].strip(';') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                elif ((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='TN') & (cnty1[pos4]!='MS;')
                      & (cnty1[pos4]!='Counties,') & (pos4>=10)):
                    crime_list.append(stat3[0].strip(';') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)

                pos4+=1
                  
        elif(state_name1 == 'Minneapolis-St. Paul-Bloomington, MN-WI M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
            
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[1].strip(',3')+ ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[2].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[3].strip(',')+ ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[4].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[5].strip(',')+ ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[6].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[7].strip(',')+ ' ' +cnty1[8].strip(',')+":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[9].strip(',')+ ' ' +cnty1[10].strip(',')+":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[11].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[12].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[13].strip(',') + ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[14].strip(',') + ":" + listToStr)
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[20].strip(',') + ":" + listToStr)
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[22].strip(',')+ ' ' +cnty1[23].strip(',')+":" + listToStr)

        elif(state_name1 == 'Myrtle Beach-Conway-North Myrtle Beach, SC-NC M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
                  
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[1].strip(',')+ ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[5].strip(',') + ":" + listToStr)

        elif(state_name1 == 'Omaha-Council Bluffs, NE-IA M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
        
            pos4 = 0
        
            while(pos4<len(cnty1)):
                if((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='Counties,') & (pos4<5)):
                    crime_list.append(stat3[1].strip('3') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                elif ((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='IA') & (cnty1[pos4]!='NE')
                      & (cnty1[pos4]!='Counties,') & (pos4>=5)):
                    crime_list.append(stat3[0].strip() + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                pos4+=1
 
        elif(state_name1 == 'Portland-Vancouver-Hillsboro, OR-WA M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
        
            pos4 = 0
        
            while(pos4<len(cnty1)):
                if((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='Counties,') & (pos4<6)):
                    crime_list.append(stat3[0].strip('3') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                elif ((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='OR') & (cnty1[pos4]!='WA')
                      & (cnty1[pos4]!='Counties,') & (pos4>=6)):
                    crime_list.append(stat3[1].strip() + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                pos4+=1

        elif(state_name1 == 'Providence-Warwick, RI-MA M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
        
            pos4 = 0
        
            while(pos4<len(cnty1)):
                if((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='Counties,') & (pos4<2)):
                    crime_list.append(stat3[1].strip('3') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                elif ((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='RI') & (cnty1[pos4]!='MA')
                      & (cnty1[pos4]!='Counties,') & (pos4>=2)):
                    crime_list.append(stat3[0].strip() + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                pos4+=1

        elif(state_name1 == 'Salisbury, MD-DE M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
        
            pos4 = 0
        
            while(pos4<len(cnty1)):
                if((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='Counties,') & (pos4<2)):
                    crime_list.append(stat3[1].strip('3') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                elif ((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and') & (cnty1[pos4]!='DE') & (cnty1[pos4]!='MD')
                     & (cnty1[pos4]!='Counties,') & (pos4>=2)):
                    crime_list.append(stat3[0].strip() + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                pos4+=1

        elif(state_name1 == 'Sioux City, IA-NE-SD M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[1].strip(',')+ ":" + listToStr)
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[4].strip(',')+ ":" + listToStr)
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[6].strip(',')+ ":" + listToStr)
            crime_list.append(stat3[2].strip(';') + ":" + cnty1[10].strip(',')+ ":" + listToStr)

        elif(state_name1 == 'St. Joseph, MO-KS M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[1].strip(',')+ ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[5].strip(',')+ ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[6].strip(',')+ ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[8].strip(',')+ ":" + listToStr)

        elif(state_name1 == 'Texarkana, TX-AR M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[1].strip(',')+' ' +cnty1[2].strip(',')+":" + listToStr)
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[4].strip(',')+ ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[8].strip(',')+ ":" + listToStr)
            
        elif(state_name1 == 'Virginia Beach-Norfolk-Newport News, VA-NC M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
            
            pos4 = 0
            while(pos4<4):
                if((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and')):
                    crime_list.append(stat3[1].strip('3') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                pos4+=1
            
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[8].strip(',')+ ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[9].strip(',')+' ' +cnty1[10].strip(',')+' '+cnty1[11].strip(',')+":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[12].strip(',')+' ' +cnty1[13].strip(',')+":" + listToStr)
        
            pos4=14
            while(pos4<28):
                if((cnty1[pos4]!='Includes') & (cnty1[pos4]!='and')):
                    crime_list.append(stat3[0].strip('3') + ":" + cnty1[pos4].strip(',')+ ":" + listToStr)
                pos4+=1

            crime_list.append(stat3[0].strip(';') + ":" + cnty1[29].strip(',')+' ' +cnty1[30].strip(',')+":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[32].strip(',')+":" + listToStr)

        elif(state_name1 == 'Washington-Arlington-Alexandria, DC-VA-MD-WV M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
             # print(cnty1)
             # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                 v = values1[x].split(' ')
                 for k in v:
                     v1.append(k)
                 x+=1
                 listToStr = ':'.join(map(str, v1))

        elif(state_name1 == 'Weirton-Steubenville, WV-OH M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                     v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[1].strip(',')+ ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[5].strip(',')+ ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[7].strip(',')+ ":" + listToStr)

        elif(state_name1 == 'Winchester, VA-WV M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[1].strip(',')+ ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[4].strip(',')+ ' '+cnty1[5].strip(',')+ ":" + listToStr)
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[8].strip(',')+ ":" + listToStr)

        elif(state_name1 == 'Worcester, MA-CT M.S.A.'):
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            stat3 = stat2[1].split("-")
            cnty1 = county_name1.strip().split(" ")
            # print(cnty1)
            # pos2 = 0
            v1=[]
            x = 2
            while(x<len(values1)):
                v = values1[x].split(' ')
                for k in v:
                    v1.append(k)
                x+=1
                listToStr = ':'.join(map(str, v1))
            crime_list.append(stat3[1].strip(';') + ":" + cnty1[1].strip(',')+ ":" + listToStr)
            crime_list.append(stat3[0].strip(';') + ":" + cnty1[5].strip(',')+ ":" + listToStr)

#For other M.S.A.s, which comprises of only a single particular State
         
        else:
            stat1 = state_name1.split(',')
            stat2 = stat1[1].split(" ")
            cnty1 = county_name1.split(",")
            if(stat2[1] == 'Puerto'):
                stat2[1]= 'Puerto Rico'
                pos2 = 0
                v1=[]
                x = 2
                while(x<len(values1)):
                    v = values1[x].split(' ')
                    for k in v:
                        v1.append(k)
                    x+=1
                    listToStr = ':'.join(map(str, v1))
                while(pos2<len(cnty1)):
                    if(len(cnty1[pos2].strip().split(' ')) == 1):
                        crime_list.append(stat2[1].strip() + ":" + cnty1[pos2].strip() + ":"+ listToStr)
                    else:
                        cnty2 = cnty1[pos2].strip().split(' ')
                        pos3 =0;
                        while(pos3<len(cnty2)):
                            if((cnty2[pos3] == 'San')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip()+ ":"+ listToStr)
                                pos3+=1
                            
                            elif((cnty2[pos3] == 'Las')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip()+ ":"+ listToStr)
                                pos3+=1

                            elif((cnty2[pos3] == 'Juana')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+":"+ listToStr)
                                pos3+=1                             

                            elif((cnty2[pos3] == 'Cobo')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+":"+ listToStr)
                                pos3+=1                             

                            elif((cnty2[pos3] == 'Sabana')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+":"+ listToStr)
                                pos3+=1                             

                            elif((cnty2[pos3] == 'Aguas')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+":"+ listToStr)
                                pos3+=1                             

                            elif((cnty2[pos3] == 'Rio')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+":"+ listToStr)
                                pos3+=1                             

                            elif((cnty2[pos3] == 'Toa')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+":"+ listToStr)
                                pos3+=1       
                            
                            elif((cnty2[pos3] == 'Trujillo')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+":"+ listToStr)
                                pos3+=1                             

                            elif((cnty2[pos3] == 'Vega')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+":"+ listToStr)
                                pos3+=1                             

                        
                            elif ((cnty2[pos3] != 'Includes') & (cnty2[pos3] != 'and') & (cnty2[pos3] != ',')
                                & (cnty2[pos3] != 'Counties') & (cnty2[pos3] != 'County') 
                                & (cnty2[pos3] != 'Municipios') & (cnty2[pos3] != 'Municipality')
                                & (cnty2[pos3] != 'Counties3') & (cnty2[pos3] != 'County3')
                                & (cnty2[pos3] != '3') & (cnty2[pos3] != 'County4') & (cnty2[pos3] != 'Borough')
                                & (cnty2[pos3] != 'GA3') & (cnty2[pos3] != 'City')& (cnty2[pos3] != 'the')
                                & (cnty2[pos3] != 'Metropolitan') & (cnty2[pos3] != 'Divisions') & (cnty2[pos3] != 'of')):
                                    crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() + ":"+ listToStr)
                            pos3+=1
                    pos2+=1
                
            else:
                cnty1 = county_name1.split(",")
                pos2 = 0
                v1=[]
                x = 2
                while(x<len(values1)):
                    v = values1[x].split(' ')
                    for k in v:
                        v1.append(k)
                    x+=1
                    listToStr = ':'.join(map(str, v1))
                while(pos2<len(cnty1)):
                    if(len(cnty1[pos2].strip().split(' ')) == 1 & (cnty1[pos2] != 'Cities' )):
                        crime_list.append(stat2[1].strip() + ":" + cnty1[pos2].strip() + ":"+ listToStr)
                    else:
                        cnty2 = cnty1[pos2].strip().split(' ')
                        pos3 =0;
                        while(pos3<len(cnty2)):
                            if((cnty2[pos3] == 'St.')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip()+ ":"+ listToStr)
                                pos3+=1
                            
                            elif((cnty2[pos3] == 'El')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+ ":"+ listToStr)
                                pos3+=1

                            elif((cnty2[pos3] == 'San')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+ ":"+ listToStr)
                                pos3+=1

                            elif((cnty2[pos3] == 'New')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+ ":"+ listToStr)
                                pos3+=1

                            elif((cnty2[pos3] == 'Cape')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+ ":"+ listToStr)
                                pos3+=1

                            elif((cnty2[pos3] == 'Box')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+ ":"+ listToStr)
                                pos3+=1
                            
                            elif((cnty2[pos3] == 'Santa')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+ ":"+ listToStr)
                                pos3+=1

                            elif((cnty2[pos3] == 'Salt')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+ ":"+ listToStr)
                                pos3+=1

                            elif((cnty2[pos3] == 'Tom')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+ ":"+ listToStr)
                                pos3+=1
 
                            elif((cnty2[pos3] == 'Contra')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+ ":"+ listToStr)
                                pos3+=1

                            elif((cnty2[pos3] == 'Indian')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+ ":"+ listToStr)
                                pos3+=1

                            elif((cnty2[pos3] == 'De')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+' Parishes'+ ":"+ listToStr)
                                pos3+=1                             
                        
                            elif((cnty2[pos3] == 'Twin')):
                               crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+":"+ listToStr)
                               pos3+=1                             

                            elif((cnty2[pos3] == 'Walla')):
                                crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() +' '+ cnty2[pos3+1].strip('3')+":"+ listToStr)
                                pos3+=1                             



                            elif ((cnty2[pos3] != 'Includes') & (cnty2[pos3] != 'and') & (cnty2[pos3] != ',')
                                & (cnty2[pos3] != 'Counties') & (cnty2[pos3] != 'County')
                                & (cnty2[pos3] != 'Municipios') & (cnty2[pos3] != 'Municipality')
                                & (cnty2[pos3] != 'Counties3') & (cnty2[pos3] != 'County3')
                                & (cnty2[pos3] != '3') & (cnty2[pos3] != 'County4') & (cnty2[pos3] != 'Borough')
                                & (cnty2[pos3] != 'GA3') & (cnty2[pos3] != 'City') & (cnty2[pos3] != 'the')
                                & (cnty2[pos3] != 'Metropolitan') & (cnty2[pos3] != 'Divisions') & (cnty2[pos3] != 'of')
                                & (cnty2[pos3] != '4') & (cnty2[pos3] != 'Parishes') & (cnty2[pos3] != 'Cities')):
                        
                                    crime_list.append(stat2[1].strip() + ":" + cnty2[pos3].strip() + ":"+ listToStr)
                        
                            pos3+=1
                    pos2+=1
        pos+=1

    for k in crime_list:
    # print(k)
        fout.write(k+'\n')
#Finally, crime_list is appended to the main Crime Data List-crime_data_final

    crime_data_final=[]
    for k in crime_list:
        crime_data_final.append(k.split(":"))

    fout.close()
# print(crime_data_final)

#Debug
    # print(test)

    # print(test[0])
    # pos3 = 0
    # while(pos3<len(test)):
    #     test1 = test[pos3].strip().split(":")
    #     if(test1[0] == 'NY'):
    #         print(test1[1])
    #     pos3+=1      

#--------------------------------------------------------------------------
#The aforementioned crime data list of lists  is converted to a dataframe
#for better accessibility and is converted to a text file    
#--------------------------------------------------------------------------
    crime_data_df = pd.DataFrame(crime_data_final)

    crime_data_df.columns = ['State','County','Violent Crime', 'Murder and Nonnelligent Manslaughter',
                             'Rape', 'Robbery','Aggravated Assault', 'Property Crime', 'Burglary',
                             'Larcency-Theft', 'Motor Vehicle Theft']
    
    crime_data_df.to_csv('crimedata_csv_original.csv',header=False, index=False)
    crime_data_df.to_csv('crimedata_csv_original_header.csv',header=True, index=False)

    # print(crime_data_df)

    crime_data_df['Violent Crime'] = crime_data_df['Violent Crime'].replace('', np.nan).replace(np.nan, 0)
    crime_data_df['Murder and Nonnelligent Manslaughter'] = crime_data_df['Murder and Nonnelligent Manslaughter'].replace('', np.nan).replace(np.nan, 0)
    crime_data_df['Robbery'] = crime_data_df['Robbery'].replace('', np.nan).replace(np.nan, 0)
    crime_data_df['Aggravated Assault'] = crime_data_df['Aggravated Assault'].replace('', np.nan).replace(np.nan, 0)
    crime_data_df['Property Crime'] = crime_data_df['Property Crime'].replace('', np.nan).replace(np.nan, 0)
    crime_data_df['Burglary'] = crime_data_df['Burglary'].replace('', np.nan).replace(np.nan, 0)
    crime_data_df['Larcency-Theft'] = crime_data_df['Larcency-Theft'].replace('', np.nan).replace(np.nan, 0)
    crime_data_df['Motor Vehicle Theft'] = crime_data_df['Motor Vehicle Theft'].replace('', np.nan).replace(np.nan, 0)

    crime_data_df['Violent Crime'] = crime_data_df['Violent Crime'].str.replace(",",'').astype(float)
    crime_data_df['Murder and Nonnelligent Manslaughter'] = crime_data_df['Murder and Nonnelligent Manslaughter'].str.replace(",",'').astype(float)
    crime_data_df['Robbery'] = crime_data_df['Robbery'].str.replace(",",'').astype(float)
    crime_data_df['Aggravated Assault'] = crime_data_df['Aggravated Assault'].str.replace(",",'').astype(float)
    crime_data_df['Property Crime'] = crime_data_df['Property Crime'].str.replace(",",'').astype(float)
    crime_data_df['Burglary'] = crime_data_df['Burglary'].str.replace(",",'').astype(float)
    crime_data_df['Larcency-Theft'] = crime_data_df['Larcency-Theft'].str.replace(",",'').astype(float)
    crime_data_df['Motor Vehicle Theft'] = crime_data_df['Motor Vehicle Theft'].str.replace(",",'').astype(float)
    
    scaler = MinMaxScaler()

    crime_data_df[['Violent Crime',
                   'Murder and Nonnelligent Manslaughter',
                   'Rape', 'Robbery','Aggravated Assault',
                   'Property Crime','Burglary','Larcency-Theft',
                   'Motor Vehicle Theft']] = scaler.fit_transform(crime_data_df[['Violent Crime',
                                                                                 'Murder and Nonnelligent Manslaughter',
                                                                                 'Rape', 'Robbery',
                                                                                 'Aggravated Assault','Property Crime',
                                                                                 'Burglary','Larcency-Theft',
                                                                                 'Motor Vehicle Theft']])

    # print(crime_data_df)
       
    crime_data_df.to_csv('crimedata_csv_scaled.csv',header=False, index=False)
    return crime_data_df

#--------------------------------------------------------------------------
#Function to return the crime index for the states sent as input
#--------------------------------------------------------------------------

def crime_rate(states):
    # loadCrimeData()
    finCrimeData1 = open(path+'crimedata_csv_scaled.csv','rt', encoding = 'utf-8')
    result =[]
    finCrimeData = csv.reader(finCrimeData1)
    for item in finCrimeData:
        for s in states:
            if(item[0] == s):
                tempdata = {}
                tempdata['State'] = item[0]
                tempdata['CountyName'] = item[1]
                
#------------Crime Index Calculation-------------
#Ranking for different crimes to assign their weightage
#Crime:Rank:Weightage (format)
#Violent Crime:1:9
#Murder and Nonnelligent Manslaughter:2:8
#Rape:3:7
#Motor Vehicle Theft:4:6
#Aggravated Assault:5:5
#Robbery:6:4
#Larcency-Theft:7:3
#Burglary:8:2
#Property Crime:9:1
#Crime Index Range = 0-5 with 0 being lowest and 5 being highest

                if (item[2] == ''):
                    vc = 0
                else:
                    vc = (float(item[2])*9)
                if (item[3] == ''):
                    mnm = 0
                else:
                    mnm = (float(item[3])*8)
                if (item[4] == ''):
                    rape = 0
                else:
                    rape = (float(item[4])*7)
                if (item[10] == ''):
                    mvt = 0
                else:
                    mvt = (float(item[10])*6)
                if (item[6] == ''):
                    aa = 0
                else:
                    aa = (float(item[6])*5)
                if (item[5] == ''):
                    rob = 0
                else:
                    rob = (float(item[5])*4)
                if (item[9] == ''):
                    lt = 0
                else:
                    lt = (float(item[9])*3)
                if (item[8] == ''):
                    burg = 0
                else:
                    burg = (float(item[8])*2)
                if (item[7] == ''):
                    pc = 0
                else:
                    pc = (float(item[7])*1)               
                        
                calc_total = vc + mnm + rape + mvt + aa + rob + lt + burg + pc
                crime_index = calc_total/9
                tempdata['Crime Index'] =round(crime_index)
                result.append(tempdata)

    crime_data_df_selected = pd.DataFrame(result)
    crime_data_df_selected.columns = ['State','County','Crime Index']
    # print(crime_data_df_selected)

    crime_data_df_selected.to_csv(path+'crimedata_selected_header.csv',header=True, index=False)
    crime_data_df_selected.to_csv(path+'crimedata_selected.csv',header=False, index=False)           
                              
    return result 
       
#test def crime_rate(states)
# print(crime_rate(['TX']))
# crime_rate(['LA'])
#load Crime Data
# loadCrimeData()





