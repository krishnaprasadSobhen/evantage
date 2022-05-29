# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 17:42:18 2021

@author:
    Yoshinori Ushiyama(yushiyam)    
    Tapasya Maji(tmaji)
    Krishnaprasd Sobhen(ksobhen)

This program scrape the pandemic data of states and counties
from The New York Times site,
(source:https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html)

Output:
     nyt_pandemic_data_state_raw.txt
     nyt_pandemic_data_state_county_raw.txt

For load the output files with "nyt_pandemic_data.py"
Please rename the file names like following:

     nyt_pandemic_data_state.txt
     nyt_pandemic_data_state_county.txt


"""
import os
path=os.path.dirname(__file__)

from selenium import webdriver
from time import sleep
def pandemicScrapper():
    fout1 = open(path+'./data/nyt_pandemic_data_state.txt',
                'wt',
                encoding = 'utf-8')
    
    fout2 = open(path+'./data/nyt_pandemic_data_state_county.txt',
                'wt',
                encoding = 'utf-8')
    
    
    #headless mode
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_argument('--headless')
    
    
    browser = webdriver.Chrome(os.path.join(path,'../chromedriver.exe'), options=options)  #headless mode
    # browser = webdriver.Chrome(os.path.join(path,'../chromedriver.exe'))  #non-headless mode
    url = 'https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html'
    browser.get(url)
    
    
    sleep(10)
    showall = browser.find_elements_by_xpath('//button[@class="expand svelte-1a4y62p"]')
    browser.execute_script("arguments[0].click();", showall[0])
    
    
    #ONLY states
    #pick up data
    data1 = browser.find_elements_by_tag_name("span")
    
    start = False
    for v in data1:
        if v.text.replace('›','').strip() == 'New York':
            start = True
        if (start == True) & (v.text != "") & (v.text.strip()[:5] != 'March') & (v.text.strip() != '–'):
            print(v.text.replace('›','').replace('<','').replace(',','').strip())
            fout1.write(v.text.replace('›','').replace('<','').replace(',','').strip() + '\n')
        if v.text.replace('›','').strip() == 'American Samoa':
            start = False
            break
    
    
    
    #states + counties
    
    #for states do not click these elems
    #for including counties, do click the toggle bottuns
    sleep(10)
    elems = browser.find_elements_by_xpath('//span[@class="show-hide svelte-1icuyd0"]')
    
    # for debug (status check of toggle buttons on the site)
    for v in elems:
        print('before click toggle buttons: ' + v.text)  # for debug
    
    for v in elems:
        browser.execute_script("arguments[0].click();", v)
        print('after click toggle buttons: ' + v.text)  # for debug
        break # ask yoshinori
    
    
    #pick up data
    data2 = browser.find_elements_by_tag_name("span")
    
    start = False
    for v in data2:
        if v.text.replace('›','').strip() == 'New York':
            start = True
        if (start == True) & (v.text != "") & (v.text.strip()[:5] != 'March') & (v.text.strip() != '–'):
            print(v.text.replace('›','').replace('<','').replace(',','').strip())
            fout2.write(v.text.replace('›','').replace('<','').replace(',','').strip() + '\n')
        if v.text.replace('›','').strip() == 'American Samoa':
            start = False
            break
    
    fout1.close()
    fout2.close()
    browser.quit()
 