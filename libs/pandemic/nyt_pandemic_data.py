# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 20:06:11 2021

@author: 
    Yoshinori Ushiyama(yushiyam)    
    Tapasya Maji(tmaji)
    Krishnaprasd Sobhen(ksobhen)
    

This is the program to crean the raw pandamic data which was
scraped by following tools
   - nyt_pandemic_selenium_states.py
   - nyt_pandemic_selenium_states_counties
And, provide the function to return counties and their risk level,
based on inputed list of states abbriviations.

@input files: 
    states' raw data,         : nyt_pandemic_data_state.txt
    counties' raw data,       : nyt_pandemic_data_state_county.txt
    states' abbreviation data : states_abbreviation.csv (source: https://github.com/jasonong/List-of-US-States/blob/master/states.csv)

@function:
    def loadPandemicData():
    return: List of countries' Pandemic records
    e.g. 'VT:Orange:516:1786:2:5', 
    [State]:[CountyName]:[Total case]:[Total Per 100000]:[Daily Avg in Last 7 days]:[Avg Per 100000]
    
    def pandemicRisk([list of states abbreviation],[list of counties' Pandemic records']):
        #e.g. states = ['PA','CA','AL']
    return: List of dictionaries
    [{state:'PA', countyName: 'plm1', risk index: '1'},
     {state:'PA', countyName: 'plm2', risk index: '2'},..,
     {state:'CA', countyName: 'clm1', risk index: '5'},..,
     {state:'AL', countyName: 'alm1', risk index: '5'},..]
     
@risk index:
    [5]extremely high risk: more than 45 cases / 100,000 people
    [4]very high risk:      more than 11 cases / 100,000 people
    [3]high risk:           more than  3 cases / 100,000 people
    [2]medium risk:         more than  1 case  / 100,000 people
    [1]low risk:            more than  0 case  / 100,000 people

@Update history:
    Mar 5, 2021 create this file to creaning raw data of pandemic and "pandemicRisk funtion"
    Mar 7, 2021 Add "loadPandemicData funtion" to make the files loading timing once
    Mar 7, 2021 Add Changed the logic to skip 'Unknown' records
    Mar 8, 2021 Modified states' record check

"""
import os
path=os.path.dirname(__file__)+'./data/'

def pandemicRisk(states, countiesPanData):
    #argment states: list of states = ['PA','CA','AL']
    #argment countiesPanData: list of counties' pandemic data created by loadPandemicData function  
    result = []
    for v in states:
        for c in countiesPanData:  #e.g. TX:Yoakum:863:9905:0:2
            elems = c.split(':')
            
            if v.strip() == elems[0].strip():
                tempDic = {}
                tempDic['state'] = elems[0]
                tempDic['countyName'] = elems[1]

                #risk calculation
                try:
                    if int(elems[5]) > 45:
                        riskIDX = 5
                    elif int(elems[5]) > 11:
                        riskIDX = 4
                    elif int(elems[5]) > 3:
                        riskIDX = 3               
                    elif int(elems[5]) > 1:
                        riskIDX = 2
                    else:
                        riskIDX = 1                        
                except:                       
                        riskIDX = 1   
                tempDic['riskIndex'] = riskIDX
                result.append(tempDic)
    return result


#loadPandemicData function load the pandemic raw data files and 
#return list of all counties' pandemic records with State abbreviations

def loadPandemicData():
    # read raw data for cleaning
    # states raw data
    finS = open(path+'nyt_pandemic_data_state.txt',
                'rt',
                encoding = 'utf-8')
    
    # counties raw data
    finC = open(path+'nyt_pandemic_data_state_county.txt',
                'rt',
                encoding = 'utf-8')
    
    # abbreviations of states & create dictionary of states, abbreciation
    finA = open(path+'states_abbreviation.csv',
                'rt',
                encoding = 'utf-8')
    
    abbreviations = {}  #e.g.{'alabama':'AL', ...}
    for v in finA:
        stateCode = v.replace('"', '').split(',')
        abbreviations[stateCode[0].lower().strip()] = stateCode[1].strip()
    
    #for debug
    fout = open(path+'nyt_pandemic_clean_data.txt',
                'wt',
                encoding = 'utf-8')
    
    
    
    #concatenate state records 'StateName:9999:9999:999:999'
#    template1 = '{0:}:{1:}:{2:}:{3:}:{4:}\n'
    template1 = '{0:}:{1:}:{2:}\n'
    cnt = 0
    states = []
    for line in finS:
        if (line.strip()[:5] != 'March') & (line.strip() != '+'):
           if cnt == 0:
               elem0 = line.strip()
               cnt += 1
           elif cnt == 1:
               elem1 = line.strip()
               cnt += 1
           elif cnt == 2:
               elem2 = line.strip()
               cnt += 1
           elif cnt == 3:
               elem3 = line.strip()
               cnt += 1
           elif cnt == 4:
               elem4 = line.strip()
               #state = template1.format(elem0, elem1, elem2, elem3, elem4)
               state = template1.format(elem0, elem3, elem4)
               states.append(state)
               cnt = 0
    
#    for v in states:  # for debug
#        print(v)


    #concatenate county records
    #there is Unknown records, if encounte "Unknown", ignores 5 lines
    #If encounter state's record, store the state and add following records
    template2 = '{0:}:{1:}:{2:}:{3:}:{4:}:{5:}\n'
    cnt = 0
    counties = []
    unknown = False
    
    for line in finC:
        if line.strip() == 'Unknown': #Unknown record case
            unknown = True
            cnt += 1
        
        elif (line.strip() == '–') | (line.strip() == '') :
            pass
           
        elif unknown == True: #Unknown record case (ignore 4 lines)
            cnt += 1
            if cnt == 5:
                unknown = False
                cnt = 0
        
        #Normal record case
        elif (unknown == False) & (line.strip()[:5] != 'March') & (line.strip() != '+'):
     
            if cnt == 0:
                elem0 = line.strip()
                cnt += 1
            elif cnt == 1:
                elem1 = line.strip()
                cnt += 1
            elif cnt == 2:
                elem2 = line.strip()
                cnt += 1
            elif cnt == 3:
                elem3 = line.strip()
                cnt += 1
            elif cnt == 4:
                elem4 = line.strip()
               
                #check if state record?
                #if state record, do not add to counties
                #but input State abbreviation to ele5
                stateFormat = template1.format(elem0, elem3, elem4)
                stateChk = False   
    
                for v in states:                                      
                    if v.lower().strip() == stateFormat.lower().strip():
                        stateChk = True
               
                if stateChk == True:
                    #serach abbreviation of the state
                    stateName = stateFormat.split(':')
                    for s in abbreviations.keys():
                        if s == stateName[0].lower():
                            elem5 = abbreviations[s]  #input it to elem5
                else:
                    #e.g.'ST:CountyName:9999:9999:999:999'
                    county = template2.format(elem5, elem0, elem1, elem2, elem3, elem4)
                    counties.append(county)
                cnt = 0
                    
    for v in counties:  # for debug
    #    print(v)
        fout.write(v) 

             
    finA.close()
    finS.close()
    finC.close()
    fout.close()  # for debug
    return counties


#Testing codes run just when this module runs as '__main__'.
if __name__ == '__main__': # for debug
    counties = loadPandemicData() 
    for c in counties:
        print(c)
    print(pandemicRisk(['PA','TX','CA','NY'], counties)) 
           
           
           
           
           

 