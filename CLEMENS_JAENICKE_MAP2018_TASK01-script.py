# MAP Geoprocessing in python (SoSe2018)
# Clemens Jänicke
# github Repo: https://github.com/clejae

#### LOAD PACKAGES ####

import gdal
import numpy as np
import ogr
import os
import osr
import random
import time

from geotools import geogen         #load package from github
from geotools import georas         #load package from github

#### WORKING DIRECTORY & GLOBAL VARIABLES ####

starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

os.chdir('C:/Users/Clemens Jänicke/Python/Uni/data/MAP/Task01_data/')
wd = 'C:/Users/Clemens Jänicke/Python/Uni/data/MAP/Task01_data/'

filePre = "CLEMENS_JAENICKE_MAP-task01"     # file name preposition
nPoints = 2                                 # number of points per stratum

#### LOAD DATA ####

vcf = gdal.Open('2000_VCF/20S_070W.tif')

# get the pathnames of all necessary filey
compositesList = geogen.GetFilesinFolderWithEnding('2015_L8_doy015/', '.bsq', True)
metricsList = geogen.GetFilesinFolderWithEnding('2015_L8_metrics/','.bsq', True)
vhmeanList = geogen.GetFilesinFolderWithEnding('2015_S1_metrics/VH_mean/', '.tif', True)
vvmeanList = geogen.GetFilesinFolderWithEnding('2015_S1_metrics/VV_mean/', '.tif', True)

# load rasters in lists
composites = georas.OpenRasterFromList(compositesList)
metrics = georas.OpenRasterFromList(metricsList)
vhmeans = georas.OpenRasterFromList(vhmeanList)
vvmeans = georas.OpenRasterFromList(vvmeanList)

# create list of raster lists
rastersList = [composites, metrics, vhmeans, vvmeans]

#### PROCESSING ####

# Check Projections
# create list of all projections
prList = [vcf.GetProjection()]
for raster in composites:
    prList.append(raster.GetProjection())
for raster in metrics:
    prList.append(raster.GetProjection())
for raster in vhmeans:
    prList.append(raster.GetProjection())
for raster in vvmeans:
    prList.append(raster.GetProjection())

# get unique values of this list
prSet = set(prList)
print("Number of different Projections: " + str(len(prSet)))

print("The Projections are: ")              # vcf has different projection compared to the others
for pr in prSet:                            # there is a slight variation between the projections of landsat and sentinel,
    print(pr)                               # but it is neglectable

# extract Spatial References
vcfSR = georas.SpatialReferenceFromRaster(vcf)
otherSR = georas.SpatialReferenceFromRaster(composites[0])

# Get total extents of Landsat and Sentinel Rasters
extentList = []
for raster in compositesList:
     corners = georas.GetCorners(raster) #order of output minx, miny, maxx, maxy
     extentList.append(corners)

# transform the extents, so that all minx, miny, maxx and maxy values form seperated lists
extentListRev = []
for i in range(len(extentList[0])):
    subList = []
    for j in range(len(extentList)):
        subList.append(extentList[j][i])
    extentListRev.append(subList)

# extract the relevant values of the total extent: minx, miny, maxx, maxy
finalExtent = [min(extentListRev[0]),min(extentListRev[1]),max(extentListRev[2]),max(extentListRev[3])]
print("Extent of Landsat and Sentinel mosaics: \n" + "Xmin: " + str(finalExtent[0]) + " Xmax: " + str(finalExtent[2]) + " Ymin: " + str(finalExtent[1])+ " Ymax: " + str(finalExtent[1]))

# create empty layer to save points
print("Starting random point sampling:")
outShapefile = filePre+"_randomPoints.shp"
outDriver = ogr.GetDriverByName("ESRI Shapefile")
# Remove output shapefile if it already exists
if os.path.exists(wd+outShapefile):
    outDriver.DeleteDataSource(outShapefile)
# Create the output shapefile
outDS = outDriver.CreateDataSource(outShapefile)
outName = filePre+"_randomPoints"
outLayer = outDS.CreateLayer(outName,vcfSR,  geom_type=ogr.wkbPoint)
# Add Fields
outLayer.CreateField(ogr.FieldDefn("UID", ogr.OFTInteger))
outLayer.CreateField(ogr.FieldDefn("VCF", ogr.OFTReal))

# Create a Random Point Sample
# lists for random sampling per stratum
stratum20 = []
stratum40 = []
stratum60 = []
stratum80 = []
stratum100 = []
totalPoints = []

# extraction list
extrList = []

count = 0
while count < 5 * nPoints:
    subList = []

    # draw random coordinates with the SRS of the composites
    randX = random.uniform(finalExtent[0],finalExtent[2])
    randY = random.uniform(finalExtent[1],finalExtent[3])

    # add these coordinates to a point Geometry
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(randX,randY)

    # transform the point to the SRS of the VCF-raster
    point.Transform(osr.CoordinateTransformation(otherSR, vcfSR))
    pointX, pointY = point.GetX(), point.GetY()

    # extract the value of the VCF-raster at the location of the point
    gt = vcf.GetGeoTransform()
    pX = int((pointX - gt[0]) / gt[1])
    pY = int((pointY - gt[3]) / gt[5])
    rb = vcf.GetRasterBand(1)
    extrValue = float(rb.ReadAsArray(pX, pY, 1, 1))

    # add the point to the sample as long as there are not enough points in each stratum
    addCheck = 0
    if extrValue <= 20:
        if len(stratum20) < nPoints:
            stratum20.append(extrValue)
            totalPoints.append(extrValue)
            addCheck += 1
    if extrValue > 20 and extrValue <= 40:
        if len(stratum40) < nPoints:
            stratum40.append(extrValue)
            totalPoints.append(extrValue)
            addCheck += 1
    if extrValue > 40 and extrValue <= 60:
        if len(stratum60) < nPoints:
            stratum60.append(extrValue)
            totalPoints.append(extrValue)
            addCheck += 1
    if extrValue > 60 and extrValue <= 80:
        if len(stratum80) < nPoints:
            stratum80.append(extrValue)
            totalPoints.append(extrValue)
            addCheck += 1
    if extrValue > 80:
        if len(stratum100) < nPoints:
            stratum100.append(extrValue)
            totalPoints.append(extrValue)
            addCheck += 1

    pointID = len(totalPoints)

    if addCheck == 1:
        print(str(pointID) + "/" + str(5 * nPoints))

        out_defn = outLayer.GetLayerDefn()      # get the layer definition
        out_feat = ogr.Feature(out_defn)        # erzeugt ein leeres dummy-feature
        out_feat.SetGeometry(point)             # packt die polygone in das dummy feature
        outLayer.CreateFeature(out_feat)        # fügt das feature zum layer hinzu

        out_feat.SetField(0, str(pointID))
        out_feat.SetField(1, extrValue)
        outLayer.SetFeature(out_feat)

        subList.append(pointID)
        subList.append(extrValue)

        # extract values from landsat and sentinel rasters
        for rasters in rastersList:                                             # loops through list of rasterlists
            for ras in rasters:                                                 # loops through rasterLists
                nBands = ras.RasterCount                                        # gets number of bands of each raster
                gt = ras.GetGeoTransform()                                      # gets gt of each raster
                pX = int((randX - gt[0]) / gt[1])                               # transform point to raster index
                pY = int((randY - gt[3]) / gt[5])
                if pY >= 0 and pY < 1000:                                           # check if pixel falls into extent of LS/Sentinel tile
                    for band in range(nBands):                                      # loops through bands of raster
                        band += 1
                        rasBand = ras.GetRasterBand(band)                           # gets band
                        if rasBand is None:
                            continue
                            print("No Band available.")
                        extrValue = float(rasBand.ReadAsArray(pX, pY, 1, 1))       # extracts value of band
                        subList.append(extrValue)
        extrList.append(subList)
        count += 1
outDS.Destroy()

# convert extraction list to array and slice x and y values out
print("Saving numpy arrays.")
totalArr = np.asarray(extrList)
xArr = totalArr[:,1]
yArr = totalArr[:,2:totalArr.shape[1]]

# write arrays out
nameXArr = filePre + "_np-array_x-values.npy"
nameYArr = filePre + "_np-array_y-values.npy"
np.save(nameXArr, xArr)
np.save(nameYArr, yArr)

print("Ready!")

endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("start: " + starttime)
print("end: " + endtime)