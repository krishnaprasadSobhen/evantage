

READ ME Manual For “EVantage”

(Instructions on how to Install and Run the application)

Prepared By -

(Python Project Group 17)

Krishnaprasad Sobhen (ksobhen@andrew.cmu.edu)

Tapasya Maji (tmaji@andrew.cmu.edu)

Yoshinori Ushiyama (yushiyam@andrew.cmu.edu)





README Manual for EVantage

\1.  Preparation of the environment for installing the application

\1. Create a new environment of Python, Anaconda and Spyder using “Anaconda Navigator”

(please do a clean install, and do not use default (base(root)) environment, because it causes

conflict error with geopandas modules)

1.1 Go to Anaconda Navigator (after an installation Anaconda3-2020.11)

1.2 Create a new environment for “EVantage” (not base(root))

1.2.1 "Environments" à Create 'EVantage”

1.2.2 "Home" and click on "Install" under the Spyder box.

1.2.3 Install Spyder for the new environment

Page 2 of 8





README Manual for EVantage

\2. (For Windows OS) : On “Anaconda Prompt”, activate the new environment “EVantage” and run

the following commands at 2.2 to install the necessary modules.

2.1 activate EVantage

(For MacOS) : On “Navigator”, to activate the new environment “EVantage” and run the

following commands to install the necessary modules.

2.1 Environments → EVantage → Open Terminal

Page 3 of 8





README Manual for EVantage

2.2 (Commands to install before running the application)

(Common for Windows and MacOS platforms)

a. conda install pandas

b. conda install shapely

c. conda install -c conda-forge selenium

d. conda install -c conda-forge geopy

e. conda install bokeh

f. conda install -c anaconda beautifulsoup4

g. conda install -c anaconda scikit-learn

h. pip install simplification

i. conda install -c anaconda xlrd

j. conda install -c anaconda requests

k. conda install -c conda-forge geopandas

l. conda install python -c conda-forge

\3. Put EVantage modules and files in the same folder (Open “EVantage.zip”).

\4. (Troubleshooting)

\-

\-

\-

If “goes\_c.dll” missing error happens.

⇨ Please install with “conda” command (not “pip”)

If “geopandas” conflicts error with other libraries happens.

⇨ Uninstall all modules and do a clean install with a new environment.

If error [Errno 22] Invalid argument:

'C:\\Users\\xxxx\\anaconda3\\envs\\xxxx\\Library\\resources\\icudtl.dat'

⇨ Close all Spyder, Jupitar book, and Anaconda prompt. Then open Anaconda prompt

again and run the install command.

\-

OSError: could not find or load spatialindex\_c-64.dll

⇨ Run the command “conda install python -c conda-forge” to match the install channel of

modules, python and geopandas.

Page 4 of 8





README Manual for EVantage

\2. To Run the Application

(Please note that for running this application, active Internet Connection is required)

\1. On “IDLE” or “Spyder” of the above set environment i.e. “EVantage”, run the python file

“group17\_evantage.py”.

The application begins to load modules and shows the below User Interface as a new window (it

may take several minutes).

\2. Enter the Start Point , Destination, the maximum radius (in terms of miles) in which the charge

stations and hotels are to be located.

For Sample Inputs for the aforementioned fields, may please click on the Sample Inputs button.

(Please note in case of any invalid inputs, i.e. the locations not found, an error message will be

populated in the UI itself and accordingly the user needs to make proper inputs.

Also as per the need i.e. to check the Pandemic Risk Index and Crime Risk Index of the counties

between the start point and the end point, please check the Pandemic Alert Map/ Crime Alert

Map box accordingly.

Page 5 of 8





README Manual for EVantage

\3. Click on Navigate Button

\4. Currently, the app uses the recently downloaded and stored data to generate the desired output.

However, if the user wants to get the live updated data, they can click on Refresh data box and

then Click the Navigate Button.

Please note that Step 4 requires approximately 1 hour to collect the live data and display the

desired output.

\5. It takes a few minutes to load and display the result data which opens as an html page in the

default internet browser of the system. The result page looks like this:

Also in the EVantage UI, the total distance, the total number of charge points and hotels is also

generated as below:

Page 6 of 8





README Manual for EVantage

The user can hover over the various points to get the details of charge points, hotels in the first map

i.e. Route Map

The user can chose the

various options on the

right hand margin of

each map to navigate,

zoom in or zoom out,

refresh the map.

Also for the Pandemic Risk Map and the Crime Risk Map, the user can hover over the selected

counties to get the risk index of those counties:

The user can chose the various options on the right hand margin of each map to navigate, zoom in or

zoom out, refresh the map.

Page 7 of 8





README Manual for EVantage

\6. To make a new search, the user needs to go back to the UI and enter the new inputs i.e. new

Start Point, Destination, the maximum radius, the Pandemic Risk and Crime Risk checks and clicks

on Navigate.

Please note before making a new search, first the previous search must be completed. Since

during the time one search (After clicking the Navigate Button) is in progress, the Navigate Button

is disabled, hence the user cannot make two simultaneous searches

\7. The application finally terminates once the user exits/ closes the EVantage UI.

\8. (Troubleshooting)

a. If “geopandas” attribute error happens;

o Check the version of geopandas. Version 0.9.0 or more is necessary.

b. In the Step 4, while user clicks on Refresh Data button to get the current data and clicks

on Navigate Button, in certain instances, it might throw an error that ‘API Key is invalid’

o This means that the API Key stored in apiKey.txt file in the charger folder (in libs

folder) needs to be updated.

For requesting a new API Key, please send a mail to : ksobhen@andrew.cmu.edu

\9. YouTube link demonstrating our project being run :

https://youtu.be/vs7JjyUtIhs (Group 17 -EVantage - Navigation App)

Bon Voyage!

Page 8 of 8

