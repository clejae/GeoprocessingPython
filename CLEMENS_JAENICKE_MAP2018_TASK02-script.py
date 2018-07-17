# MAP Geoprocessing in python (SoSe2018)
# Clemens Jänicke
# github Repo: https://github.com/clejae

#### LOAD PACKAGES ####

import ogr
import os
import osr
import time

from geotools import geovec         #load package from github
from geotools import geogen         #load package from github


#### WORKING DIRECTORY & GLOBAL VARIABLES ####

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

os.chdir('C:/Users/Clemens Jänicke/Python/Uni/data/MAP/Task02_data/')
wd = 'C:/Users/Clemens Jänicke/Python/Uni/data/MAP/Task02_data/'

filePre = "CLEMENS_JAENICKE_MAP-task02"

#### LOAD DATA ####

shpNameList = geogen.GetFilesinFolderWithEnding(wd,".shp",True)
damsShape = ogr.Open(shpNameList[0])
roadsShape = ogr.Open(shpNameList[1])
countriesShape = ogr.Open(shpNameList[2])

dams = damsShape.GetLayer()
roads = roadsShape.GetLayer()
countries = countriesShape.GetLayer()

#### PROCESSING ####

for feat in countries:
    geom = feat.GetGeometryRef()



print("Ready!")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + starttime)
print("end: " + endtime)