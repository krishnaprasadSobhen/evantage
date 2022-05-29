[1]For application use

 For get the list of counties and risk intexes of states,
 Please use following files:

  nyt_pandemic_data.py
  nyt_pandemic_data_state.txt
  nyt_pandemic_data_state_county.txt
  states_abbreviation.csv



[2]For scraping the latest pandemic data

 (Required environment)
   - Google Chrome
   - Selenium + chromedriver.exe

 When you need to scrape the latest pandemic data of each county.
 Please run the following file: [This scraping takes apploximately 2 to 3 hours]

  nyt_pandemic_selenium_states_counties.py

 This program output two files like these and when you use them in "nyt_pandemic_data.py"
 rename them (remove '_raw' from the file names)

  nyt_pandemic_data_state_raw.txt
  nyt_pandemic_data_state_county_raw.txt


[end]