# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 15:09:53 2021

@author: LENOVO
"""

from CrimeData_10032021 import loadCrimeData,crime_rate

x=loadCrimeData()
crime_rate(['TX','PA'],x)