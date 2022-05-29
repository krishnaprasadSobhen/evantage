# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 07:30:07 2021

@author: Krishnaprasd Sobhen
@version: 5.0

This application is designed to aid Electric vehicle users plan road trips with consideration of
    - Fastest route from origin to destination
    - Charging station network( proximity to route and charger type)
    - Hotels( proximity to route and rates)
    - Pandemic risk assessment
    - Crime risk assessment
    


masterModule.py is the main module of EVantage app,it comprises of two core components
    - User Inteface(UI) built on tkinter 
    - object 'eva' of class EVantage that does the backend calculation and map rendering

UI:
    -The UI is constructed as 'app' object of class Application
    -It accepts inputs like 
        -origin,destination
        -proximity values for hotel and charge points
        -map configuration
        -live data activation for webscrapping
@function:
    - navClicked - handles inputs from the UI and passes them to eva
    - setStatus - displays route statistic and warning  
    - turnONButton - turns on navigation button
    - turnOFFButton - turns off navigation button
    - resetSwitch - resets app after navigation - clears events arrising in between
    - clearInputs - clears all input fields and map options
    - sampleInputs - enters a sample input for user to test out the app
    - setDefaults - sets default configuration of UI
    - liveScrapePopUp - warning message and confirmation handler when trying to obtain live data
@version history:
    -v1 - simple ui with entries and labels
    -v2 - converting code to OOP model
    -v3 - integrating EVantage object
    -v4 - adding status block and live data options
    -v5 - handeling clicks in between execution
@ammendments-When we submitted the first version of this code we had a three typos in the file(because of a feature rollback)
            -We have fixed the same after confirming with the professor about penalty exclusion for the same
            -All changes are to display strings and are limited to this file
@change log
    -OLD FILE->CURRENT FILE
    -(line 17) evantage.py->(line 17)masterModule.py
    -(line 87) Pandmic->(line 95 )Pandemic
    -(line 94) Eneter->line 102) Enter
"""


import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg
from libs import masterModule
import numpy as np

# class for UI
class Application(ttk.Frame):

    def __init__(self, master):
        
        master.geometry("600x450")
        master.title("Welcome to EVantage")
        master.resizable(0,0)
        
        
        ttk.Frame.__init__(self, master)
        self.pandemicStatusVar = tk.BooleanVar()
        self. crimeStatusVar = tk.BooleanVar()
        self.liveScrapeVar = tk.BooleanVar()
        self.statusVar = tk.StringVar()
        self.pack()
        
        self.originEntry = tk.Entry(self,width=50)
        self.destinationEntry = tk.Entry(self,width=50)
        self.chargeRangeEntry = tk.Entry(self,width=50)
        self.hotelRangeEntry = tk.Entry(self,width=50)
        
        self.originEntry.grid(column=1, row=0,columnspan=2)
        self.destinationEntry.grid(column=1, row=1,columnspan=2)
        self.chargeRangeEntry.grid(column=1, row=2,columnspan=2)
        self.hotelRangeEntry.grid(column=1, row=3,columnspan=2)
        
        self.navigateBtn = tk.Button(self,width=25, text="Navigate",command=lambda:self.navClicked(self.originEntry.get(),self.destinationEntry.get(),self.chargeRangeEntry.get(),self.hotelRangeEntry.get()))
        self.clearBtn = tk.Button(self,width=25, text="Clear Fields",command=lambda:self.clearInputs())
        self.sampleBtn = tk.Button(self,width=15, text="Sample Inputs",command=lambda:self.sampleInputs())
        self.clearBtn.grid(column=1, row=5,sticky=tk.W)
        self.navigateBtn.grid(column=0, row=5)
        self.sampleBtn.grid(column=2, row=5,sticky=tk.W)
        
        self.pandemicBtn = tk.Checkbutton(self, text='Pandemic Alert Map',var=self.pandemicStatusVar)
        self.crimeBtn = tk.Checkbutton(self, text='Crime Alert Map',var=self.crimeStatusVar)
        self.liveBtn = tk.Checkbutton(self, text='Refresh Data',var=self.liveScrapeVar)
        self.crimeBtn.grid(column=1, row=4,sticky=tk.W)
        self.pandemicBtn.grid(column=0, row=4)
        self.liveBtn.grid(column=2, row=4,sticky=tk.W)
        
        self.originLbl = tk.Label(self, text= 'Enter your start point')
        self.destinationLbl= tk.Label(self, text= 'Enter your destination',justify=tk.LEFT, anchor="w")
        self.chargeRangeLbl = tk.Label(self, text= 'Maximum distance to charge station(miles)',justify=tk.LEFT, anchor="w")
        self.hotelRangeLbl= tk.Label(self, text= 'Maximum distance to hotel(miles)',justify=tk.LEFT, anchor="w")
        self.statusBlock = tk.Label(self, textvar=self.statusVar, borderwidth=2,height=10,width=80,relief="groove",justify=tk.LEFT, anchor="nw")
        
        self.originLbl.grid(sticky=tk.W,column=0, row=0)
        self.destinationLbl.grid(sticky=tk.W,column=0, row=1)
        self.chargeRangeLbl.grid(sticky=tk.W,column=0, row=2)
        self.hotelRangeLbl.grid(sticky=tk.W,column=0, row=3)
        self.statusBlock.grid(sticky=tk.W,column=0,columnspan=3,row=6)
        
        for child in self.winfo_children():
            child.grid_configure(padx=10, pady=10)
        
        self.eva=masterModule.EVantage()
        self.livedata=False
        self.setStatus("Status:\n Boot time : "+self.eva.convertTime(self.eva.bootTime)) # displays boot time
    def navClicked(self,startPoint,stopPoint,chargeRange,hotelRange): # handles inputs from the UI and passes them to eva
        print("Button clicked")
        if(self.liveScrapeVar.get()): # check if live data is enabled
            self.liveScrapePopUp() # get confirmation from user
            if(self.livedata==False):
                self.liveScrapeVar.set(False) # if user decilnes reset button
                return
        self.turnOFFButton() # disable button till navigation is completed
        # passing all route parameters,map configuration and live data status to eva
        status=self.eva.findLocation(startPoint,stopPoint,chargeRange,hotelRange,self.pandemicStatusVar.get(),self.crimeStatusVar.get(),self.liveScrapeVar.get())
        if(status[0]==False):# some navigation error occured
            self.setStatus(status[1]) # display error
        else:
            self.setStatus(self.eva.routeStatistics) # if routing is successful display route statistics
        self.resetSwitch() # reactivate the navigation button and clear all previous click events
        return
    def resetSwitch(self):
        self.master.update()
        self.turnONButton()
    
    def turnONButton(self):
        if (self.navigateBtn['state'] == tk.DISABLED):
            self.navigateBtn['state'] = tk.NORMAL
    def turnOFFButton(self):
        if (self.navigateBtn['state'] == tk.NORMAL):
            self.navigateBtn['state'] = tk.DISABLED
    
    def clearInputs(self):
        self.originEntry.delete(0, 'end')
        self.destinationEntry.delete(0, 'end')
        self.chargeRangeEntry.delete(0, 'end')
        self.hotelRangeEntry.delete(0, 'end')
        self.pandemicStatusVar.set(False)
        self.crimeStatusVar.set(False)
        self.liveScrapeVar.set(False)
        return
    def sampleInputs(self):
        self.clearInputs()
        self.setDefaults()
        samples=["Austin,TX","Pittsburgh,PA","Houston,TX","Cesars Palace,NV","Liberty Bell,PA"]
        places=np.random.choice(samples, size=2, replace=False) # generates random sample inputs for user from samples
        self.originEntry.insert(0,places[0])
        self.destinationEntry.insert(0,places[1])
        return
    def setDefaults(self):
        self.pandemicStatusVar.set(True)
        self.chargeRangeEntry.insert(0,"5")
        self.hotelRangeEntry.insert(0,"10")
        return
    def liveScrapePopUp(self):
        MsgBox =msg.askquestion ('Data refresh enabled','This operation may take upto an hour or more! Do you wish to continue?',icon = 'warning')
        if MsgBox == 'yes':
            self.livedata=True # set status for live data
        else:
            msg.showinfo('Disabling data refresh','Data refresh disabled')
            self.livedata=False
    def setStatus(self,statusText):
        print("Status update called :",statusText)
        self.statusVar.set(statusText)

root = tk.Tk()
app = Application(root) # ui created
app.setDefaults()
root.mainloop()
